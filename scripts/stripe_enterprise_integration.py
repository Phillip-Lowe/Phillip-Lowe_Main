#!/usr/bin/env python3
"""
SAOS Enterprise Stripe Integration
===================================
Handles Stripe checkout for Enterprise tier and auto-triggers VPS provisioning.

Usage:
    # Create/update Stripe product
    python3 stripe_enterprise_integration.py --create-product
    
    # Handle webhook (called by n8n or HTTP endpoint)
    python3 stripe_enterprise_integration.py --webhook-file webhook_payload.json
"""
import os
import sys
import json
import argparse
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# Stripe credentials (load from env or secure storage)
STRIPE_PK = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SK = os.environ.get("STRIPE_SECRET_KEY", "")

if not STRIPE_PK or not STRIPE_SK:
    # Fallback: load from secure credential file
    _cred_path = os.path.expanduser("~/.openclaw/workspaces/sol/Sol-Knowledge/Sol-Knowledge/credentials/Green/stripe/keys.json")
    if os.path.exists(_cred_path):
        with open(_cred_path) as f:
            _keys = json.load(f)
        STRIPE_PK = _keys.get("publishable key", "")
        STRIPE_SK = _keys.get("secret key", "")
    else:
        raise ValueError("Stripe credentials not found. Set env vars or provide keys.json")

# Enterprise pricing
ENTERPRISE_MONTHLY = 79900  # $799.00 in cents
ENTERPRISE_ANNUAL = 799000  # $7,990.00 in cents (2 months free)

# Webhook secret (load from env)
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_enterprise_placeholder")


def create_enterprise_product():
    """Create Stripe product and price for Enterprise tier."""
    import stripe
    stripe.api_key = STRIPE_SK
    
    print("Creating/updating Stripe Enterprise product...")
    
    try:
        # Check if product already exists
        products = stripe.Product.list(limit=10)
        enterprise_product = None
        for p in products.data:
            if p.name == "SAOS Enterprise Fleet":
                enterprise_product = p
                print(f"Found existing product: {p.id}")
                break
        
        if not enterprise_product:
            # Create product
            enterprise_product = stripe.Product.create(
                name="SAOS Enterprise Fleet",
                description="Multi-location AI operations layer with compliance",
                metadata={
                    "tier": "enterprise",
                    "vcpu": "8",
                    "ram_gb": "32",
                    "storage_gb": "320",
                    "locations": "5",
                    "compliance": "SOC2,HIPAA,GDPR"
                }
            )
            print(f"Created product: {enterprise_product.id}")
        
        # Create monthly price
        monthly_price = stripe.Price.create(
            product=enterprise_product.id,
            unit_amount=ENTERPRISE_MONTHLY,
            currency="usd",
            recurring={"interval": "month"},
            metadata={"billing_period": "monthly", "tier": "enterprise"}
        )
        print(f"Monthly price: {monthly_price.id} (${ENTERPRISE_MONTHLY/100:.2f}/mo)")
        
        # Create annual price
        annual_price = stripe.Price.create(
            product=enterprise_product.id,
            unit_amount=ENTERPRISE_ANNUAL,
            currency="usd",
            recurring={"interval": "year"},
            metadata={"billing_period": "annual", "tier": "enterprise", "discount": "2_months_free"}
        )
        print(f"Annual price: {annual_price.id} (${ENTERPRISE_ANNUAL/100:.2f}/yr)")
        
        # Generate payment links
        monthly_link = stripe.PaymentLink.create(
            line_items=[{"price": monthly_price.id, "quantity": 1}],
            metadata={"tier": "enterprise", "billing": "monthly"},
            after_completion={"type": "redirect", "redirect": {"url": "https://systack.net/payment-success?tier=enterprise"}}
        )
        print(f"Monthly payment link: {monthly_link.url}")
        
        annual_link = stripe.PaymentLink.create(
            line_items=[{"price": annual_price.id, "quantity": 1}],
            metadata={"tier": "enterprise", "billing": "annual"},
            after_completion={"type": "redirect", "redirect": {"url": "https://systack.net/payment-success?tier=enterprise"}}
        )
        print(f"Annual payment link: {annual_link.url}")
        
        # Save configuration
        config = {
            "product_id": enterprise_product.id,
            "monthly_price_id": monthly_price.id,
            "annual_price_id": annual_price.id,
            "monthly_payment_link": monthly_link.url,
            "annual_payment_link": annual_link.url,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        config_path = os.path.expanduser("~/.openclaw/workspaces/sol/Sol-Knowledge/Sol-Knowledge/credentials/Green/stripe/enterprise-config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Configuration saved: {config_path}")
        
        return config
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def handle_checkout_webhook(payload: dict):
    """Process Stripe checkout.session.completed webhook."""
    
    print("Processing Stripe checkout webhook...")
    
    # Extract session data
    session = payload.get("data", {}).get("object", {})
    if not session:
        print("❌ No session data in payload")
        return False
    
    # Verify this is for Enterprise tier
    metadata = session.get("metadata", {})
    if metadata.get("tier") != "enterprise":
        print(f"⏭️  Skipping non-enterprise tier: {metadata.get('tier', 'unknown')}")
        return False
    
    # Extract customer info
    customer_email = session.get("customer_details", {}).get("email", "")
    customer_name = session.get("customer_details", {}).get("name", "")
    client_id = metadata.get("client_id", customer_email.split("@")[0].upper())
    
    # Extract subscription/plan info
    subscription_id = session.get("subscription", "")
    billing_period = metadata.get("billing", "monthly")
    
    print(f"\n📋 Enterprise Checkout Complete")
    print(f"   Client: {client_id}")
    print(f"   Email: {customer_email}")
    print(f"   Name: {customer_name}")
    print(f"   Billing: {billing_period}")
    print(f"   Subscription: {subscription_id}")
    
    # Queue provisioning task
    task_payload = {
        "client_id": client_id,
        "customer_email": customer_email,
        "customer_name": customer_name,
        "tier": "enterprise",
        "billing_period": billing_period,
        "subscription_id": subscription_id,
        "stripe_session_id": session.get("id"),
        "compliance": metadata.get("compliance", "SOC2"),
        "locations": metadata.get("locations", "ord").split(",")
    }
    
    # Insert into task_queue
    return queue_provisioning_task(task_payload)


def queue_provisioning_task(payload: dict) -> bool:
    """Insert DEPLOY task into Postgres task_queue."""
    
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="systack_memory",
            user="systack",
            password="Systack2026!CRM"
        )
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO task_queue (task_type, payload_json, priority, status, max_retries)
            VALUES ('DEPLOY', %s::jsonb, 9, 'PENDING', 3)
            RETURNING id
        """, (json.dumps(payload),))
        
        task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n✅ Queued provisioning task #{task_id}")
        print(f"   Bridge will pick up and deploy within 30 seconds")
        return True
        
    except Exception as e:
        print(f"❌ Failed to queue task: {e}")
        return False


def verify_webhook_signature(payload: str, sig_header: str) -> bool:
    """Verify Stripe webhook signature."""
    import stripe
    stripe.api_key = STRIPE_SK
    
    try:
        stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        return True
    except Exception as e:
        print(f"⚠️  Webhook verification failed: {e}")
        return False


def generate_html_checkout_buttons():
    """Generate HTML for direct Stripe Checkout links."""
    
    config_path = os.path.expanduser("~/.openclaw/workspaces/sol/Sol-Knowledge/Sol-Knowledge/credentials/Green/stripe/enterprise-config.json")
    
    if not os.path.exists(config_path):
        print("❌ No enterprise config found. Run --create-product first.")
        return
    
    with open(config_path) as f:
        config = json.load(f)
    
    html = f"""<!-- SAOS Enterprise Checkout Buttons -->
<div class="enterprise-checkout">
    <div class="pricing-card enterprise">
        <h3>SAOS Enterprise Fleet</h3>
        <div class="price">$799<span>/month</span></div>
        <ul>
            <li>8 vCPU / 32GB RAM</li>
            <li>Up to 5 locations</li>
            <li>SOC 2, HIPAA, GDPR compliance</li>
            <li>White-label dashboard</li>
            <li>Priority support + SLA</li>
        </ul>
        <a href="{config['monthly_payment_link']}" class="btn-primary">Subscribe Monthly</a>
        <a href="{config['annual_payment_link']}" class="btn-secondary">Pay Annually (2 months free)</a>
    </div>
</div>
"""
    
    output_path = "/tmp/systack-saas-init/docs/enterprise-checkout-buttons.html"
    with open(output_path, "w") as f:
        f.write(html)
    
    print(f"✅ Checkout buttons HTML: {output_path}")
    print(f"   Monthly: {config['monthly_payment_link']}")
    print(f"   Annual: {config['annual_payment_link']}")


def main():
    parser = argparse.ArgumentParser(description="SAOS Enterprise Stripe Integration")
    parser.add_argument("--create-product", action="store_true", help="Create/update Stripe product")
    parser.add_argument("--webhook-file", type=str, help="Process webhook from JSON file")
    parser.add_argument("--generate-html", action="store_true", help="Generate checkout button HTML")
    parser.add_argument("--webhook-secret", type=str, help="Stripe webhook signing secret")
    
    args = parser.parse_args()
    
    if args.webhook_secret:
        global WEBHOOK_SECRET
        WEBHOOK_SECRET = args.webhook_secret
    
    if args.create_product:
        config = create_enterprise_product()
        print("\n📋 Enterprise Product Configuration:")
        print(json.dumps(config, indent=2))
    
    elif args.webhook_file:
        with open(args.webhook_file) as f:
            payload = json.load(f)
        handle_checkout_webhook(payload)
    
    elif args.generate_html:
        generate_html_checkout_buttons()
    
    else:
        parser.print_help()
        print("\n💡 Tip: Start with --create-product to set up Stripe products")


if __name__ == "__main__":
    main()
