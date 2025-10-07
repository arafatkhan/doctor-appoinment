import requests
import json
import uuid
from datetime import datetime
from django.conf import settings


class BkashPaymentService:
    """Service class for bKash Payment Gateway integration"""
    
    def __init__(self):
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self.base_url = settings.BKASH_BASE_URL
        self.token = None
        self.token_expiry = None
    
    def get_grant_token(self):
        """Get grant token from bKash API"""
        try:
            url = f"{self.base_url}/tokenized/checkout/token/grant"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'username': self.username,
                'password': self.password
            }
            
            data = {
                'app_key': self.app_key,
                'app_secret': self.app_secret
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('statusCode') == '0000':
                self.token = result.get('id_token')
                return self.token
            else:
                print(f"Error getting grant token: {result.get('statusMessage')}")
                return None
        
        except Exception as e:
            print(f"Error in get_grant_token: {str(e)}")
            return None
    
    def create_payment(self, amount, invoice_number, merchant_invoice_number=None):
        """
        Create a bKash payment
        
        Args:
            amount (float): Payment amount
            invoice_number (str): Unique invoice number
            merchant_invoice_number (str): Optional merchant invoice number
        
        Returns:
            dict: Payment creation response with bkashURL for redirect
        """
        try:
            if not self.token:
                self.get_grant_token()
            
            if not self.token:
                return None
            
            url = f"{self.base_url}/tokenized/checkout/create"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': self.token,
                'X-APP-Key': self.app_key
            }
            
            # Generate unique payment reference
            payment_reference = merchant_invoice_number or str(uuid.uuid4())
            
            data = {
                'mode': '0011',  # Checkout mode
                'payerReference': ' ',
                'callbackURL': 'http://localhost:8000/payment/callback/',
                'amount': str(amount),
                'currency': 'BDT',
                'intent': 'sale',
                'merchantInvoiceNumber': payment_reference
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('statusCode') == '0000':
                return {
                    'payment_id': result.get('paymentID'),
                    'bkash_url': result.get('bkashURL'),
                    'callback_url': result.get('callbackURL'),
                    'success': True,
                    'message': 'Payment created successfully'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('statusMessage', 'Payment creation failed')
                }
        
        except Exception as e:
            print(f"Error creating payment: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def execute_payment(self, payment_id):
        """
        Execute a bKash payment after user approval
        
        Args:
            payment_id (str): Payment ID from create_payment response
        
        Returns:
            dict: Execution result with transaction details
        """
        try:
            if not self.token:
                self.get_grant_token()
            
            url = f"{self.base_url}/tokenized/checkout/execute"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': self.token,
                'X-APP-Key': self.app_key
            }
            
            data = {
                'paymentID': payment_id
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('statusCode') == '0000':
                return {
                    'success': True,
                    'transaction_id': result.get('trxID'),
                    'payment_id': result.get('paymentID'),
                    'amount': result.get('amount'),
                    'customer_msisdn': result.get('customerMsisdn'),
                    'transaction_status': result.get('transactionStatus'),
                    'message': 'Payment executed successfully'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('statusMessage', 'Payment execution failed')
                }
        
        except Exception as e:
            print(f"Error executing payment: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def query_payment(self, payment_id):
        """
        Query payment status
        
        Args:
            payment_id (str): Payment ID to query
        
        Returns:
            dict: Payment status information
        """
        try:
            if not self.token:
                self.get_grant_token()
            
            url = f"{self.base_url}/tokenized/checkout/payment/status"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': self.token,
                'X-APP-Key': self.app_key
            }
            
            data = {
                'paymentID': payment_id
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            return result
        
        except Exception as e:
            print(f"Error querying payment: {str(e)}")
            return None
    
    def refund_payment(self, payment_id, transaction_id, amount, reason):
        """
        Refund a payment
        
        Args:
            payment_id (str): Original payment ID
            transaction_id (str): Transaction ID to refund
            amount (float): Refund amount
            reason (str): Refund reason
        
        Returns:
            dict: Refund result
        """
        try:
            if not self.token:
                self.get_grant_token()
            
            url = f"{self.base_url}/tokenized/checkout/payment/refund"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': self.token,
                'X-APP-Key': self.app_key
            }
            
            data = {
                'paymentID': payment_id,
                'trxID': transaction_id,
                'amount': str(amount),
                'reason': reason,
                'sku': 'refund'
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('statusCode') == '0000':
                return {
                    'success': True,
                    'refund_trx_id': result.get('refundTrxID'),
                    'message': 'Refund processed successfully'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('statusMessage', 'Refund failed')
                }
        
        except Exception as e:
            print(f"Error processing refund: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }


# Helper function for appointment payment
def initiate_appointment_payment(appointment, callback_url=None):
    """
    Initiate bKash payment for an appointment
    
    Args:
        appointment: Appointment model instance
        callback_url: Optional callback URL after payment
    
    Returns:
        dict: Payment initiation response with redirect URL
    """
    bkash_service = BkashPaymentService()
    
    invoice_number = f"APT-{appointment.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    amount = float(appointment.amount)
    
    result = bkash_service.create_payment(
        amount=amount,
        invoice_number=invoice_number
    )
    
    return result
