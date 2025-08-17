"""
Test script to verify PayPal integration
"""
import streamlit as st
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_paypal_connection():
    """Test PayPal API connection"""
    st.title("🧪 PayPal Integration Test")
    
    try:
        # Import PayPal functions from main
        from main import get_access_token, create_order, PayPalError
        
        st.success("✅ PayPal functions imported successfully")
        
        # Test credentials
        paypal_client_id = st.secrets.get("PAYPAL_CLIENT_ID", os.getenv("PAYPAL_CLIENT_ID"))
        paypal_secret = st.secrets.get("PAYPAL_SECRET", os.getenv("PAYPAL_SECRET"))
        
        if paypal_client_id and paypal_secret:
            st.success("✅ PayPal credentials found")
            
            # Test access token
            if st.button("Test PayPal Connection"):
                try:
                    with st.spinner("Testing PayPal API..."):
                        token = get_access_token()
                        if token:
                            st.success("✅ PayPal API connection successful!")
                            st.info(f"Access token received (first 20 chars): {token[:20]}...")
                        else:
                            st.error("❌ Failed to get access token")
                except PayPalError as e:
                    st.error(f"❌ PayPal Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
            
            # Test order creation
            if st.button("Test Order Creation"):
                try:
                    with st.spinner("Creating test order..."):
                        order = create_order("1.00", "USD")
                        if order.get("order_id"):
                            st.success("✅ Test order created successfully!")
                            st.json(order)
                        else:
                            st.error("❌ Failed to create test order")
                except PayPalError as e:
                    st.error(f"❌ PayPal Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
        else:
            st.error("❌ PayPal credentials not found. Please check your secrets configuration.")
            st.info("Make sure to set PAYPAL_CLIENT_ID and PAYPAL_SECRET in your Streamlit secrets.")
    
    except ImportError as e:
        st.error(f"❌ Import error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_paypal_connection()