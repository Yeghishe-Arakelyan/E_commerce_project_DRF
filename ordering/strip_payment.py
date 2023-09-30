from typing import Optional
import stripe

def stripe_payment(secret_key: str, token: str, amount: float, description: str) -> Optional[str]:
    try:
        stripe.api_key = secret_key

        charge = stripe.Charge.create(
            amount=int(amount * 100), 
            currency='usd',  
            description=description,
            source=token,
        )

        return charge['id']

    except stripe.error.StripeError as e:
       
        error_message = f"Stripe error: {e.user_message}"
        print(error_message)
        return None

    except Exception as e:
        
        error_message = f"Payment failed: {str(e)}"
        print(error_message)
        return None
