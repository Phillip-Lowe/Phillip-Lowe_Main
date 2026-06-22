/**
 * Utopia Deli — Order Form Logic v2.0 (Webhook Integration)
 * POSTs JSON to n8n webhook per WEBHOOK-DOCS.md schema
 * PLAN_ID: PLAN-HTML-WEBHOOK-INTEGRATION-2026-06-01
 * ROLE: CODY
 * Date: 2026-06-06
 *
 * Schema: customer_name, email, phone, order_items[], subtotal, tax, total,
 *         pickup_time, special_instructions, source, timestamp
 * Endpoint: https://utopia-api.systack.net/webhook/utopia-deli-html-order-v1
 */

// ── Menu Data (matches Square catalog) ─────────────────────────────────────
const MENU = [
  { id: 'cowboy-chicken',   name: "Cowboy Chik'n Sandwich",       price: 13.00, category: 'entrees' },
  { id: 'club-sub',         name: "Chik'n Club Sub",              price: 15.00, category: 'entrees' },
  { id: 'fried-sub',        name: "Chik'n Fried Chik'n Sub",      price: 13.00, category: 'entrees' },
  { id: 'philly-sub',       name: 'Philly Sub',                   price: 13.00, category: 'entrees' },
  { id: 'sliders',          name: "Rocktown Bourbon Chik'n Sliders", price: 12.00, category: 'entrees' },
  { id: 'buffalo-sliders',  name: "Buffalo Chik'n Sliders",       price: 12.00, category: 'entrees' },
  { id: 'poppers',          name: "Chik'n Poppers",               price: 10.00, category: 'entrees' },
  { id: 'tacos',            name: 'Korean "Pork" Dumpling Tacos',  price: 10.00, category: 'entrees' },
  { id: 'loaded-fries',     name: 'Loaded Fries',                 price: 13.00, category: 'sides' },
  { id: 'onion-rings',      name: 'Onion Rings',                  price:  7.50, category: 'sides' },
  { id: 'potato-chip-spirals', name: 'Potato Chip Spirals',       price:  5.00, category: 'sides' },
  { id: 'fountain-drink',   name: 'Fountain Drink',               price:  2.50, category: 'drinks' },
  { id: 'bottled-water',    name: 'Bottled Water',                price:  2.00, category: 'drinks' },
];

const TAX_RATE = 0.0952; // Arkansas state rate: 9.52%

// ── State ──────────────────────────────────────────────────────────────────
let cart = {}; // { itemId: quantity }

// ── Helpers ────────────────────────────────────────────────────────────────
function fmt$(dollars) {
  return '$' + dollars.toFixed(2);
}

function getCartItems() {
  return Object.entries(cart)
    .filter(([, qty]) => qty > 0)
    .map(([id, qty]) => {
      const item = MENU.find(m => m.id === id);
      return { ...item, quantity: qty };
    });
}

function calcTotals() {
  const items = getCartItems();
  const subtotal = items.reduce((sum, it) => sum + it.price * it.quantity, 0);
  const tax = Math.round(subtotal * TAX_RATE * 100) / 100; // Round to cents
  const total = Math.round((subtotal + tax) * 100) / 100;
  return { subtotal, tax, total, items };
}

// ── UI: Menu ─────────────────────────────────────────────────────────────────
function renderMenu() {
  const el = document.getElementById('menu-list');
  if (!el) return;

  const byCat = MENU.reduce((acc, it) => {
    acc[it.category] = acc[it.category] || [];
    acc[it.category].push(it);
    return acc;
  }, {});

  const catNames = {
    entrees: '🥪 Entrees',
    sides: '🍟 Sides',
    drinks: '🥤 Drinks'
  };

  el.innerHTML = Object.entries(byCat).map(([cat, items]) => `
    <div class="menu-category">
      <h4>${catNames[cat] || cat}</h4>
      <div class="menu-items">
        ${items.map(it => `
          <div class="menu-item" data-id="${it.id}">
            <div class="item-info">
              <span class="item-name">${it.name}</span>
              <span class="item-price">${fmt$(it.price)}</span>
            </div>
            <div class="qty-control">
              <button type="button" onclick="adjustQty('${it.id}', -1)">−</button>
              <span class="qty" id="qty-${it.id}">0</span>
              <button type="button" onclick="adjustQty('${it.id}', 1)">+</button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function adjustQty(id, delta) {
  cart[id] = (cart[id] || 0) + delta;
  if (cart[id] < 0) cart[id] = 0;
  const el = document.getElementById(`qty-${id}`);
  if (el) el.textContent = cart[id];
  renderCart();
}

// ── UI: Cart ───────────────────────────────────────────────────────────────
function renderCart() {
  const { subtotal, tax, total, items } = calcTotals();

  const cartList = document.getElementById('cart-list');
  const emptyMsg = document.getElementById('cart-empty');

  if (!cartList || !emptyMsg) return;

  if (items.length === 0) {
    cartList.innerHTML = '';
    emptyMsg.style.display = 'block';
  } else {
    emptyMsg.style.display = 'none';
    cartList.innerHTML = items.map(it => `
      <div class="cart-row">
        <span>${it.name} × ${it.quantity}</span>
        <span>${fmt$(it.price * it.quantity)}</span>
      </div>
    `).join('');
  }

  const subtotalEl = document.getElementById('subtotal');
  const taxEl = document.getElementById('tax');
  const totalEl = document.getElementById('total');
  if (subtotalEl) subtotalEl.textContent = fmt$(subtotal);
  if (taxEl) taxEl.textContent = fmt$(tax);
  if (totalEl) totalEl.textContent = fmt$(total);

  const btn = document.getElementById('submit-btn');
  if (btn) btn.disabled = items.length === 0;
}

// ── Pickup Time Options ──────────────────────────────────────────────────────
function buildPickupOptions() {
  const sel = document.getElementById('pickup-time');
  if (!sel) return;

  const now = new Date();
  const minLead = 30; // 30 min kitchen lead time
  const openHour = 12;   // 12:30 PM
  const openMin = 30;
  const closeHour = 19;  // 7:30 PM
  const closeMin = 30;

  // Start from :00 or :30 past the hour, with lead time
  let cursor = new Date(now.getTime() + minLead * 60000);

  // Round up to nearest 30 min
  const mins = cursor.getMinutes();
  if (mins <= 30) {
    cursor.setMinutes(30, 0, 0);
  } else {
    cursor.setMinutes(0, 0, 0);
    cursor.setHours(cursor.getHours() + 1);
  }

  const endToday = new Date(now);
  endToday.setHours(closeHour, closeMin, 0, 0);

  // If after hours, start tomorrow
  if (cursor > endToday) {
    cursor.setDate(cursor.getDate() + 1);
    cursor.setHours(openHour, openMin, 0, 0);
  }

  // Build next 48h of slots (Mon-Sat only, deli closed Sunday)
  const options = [];
  const maxSlots = 48;
  let slotsBuilt = 0;

  while (slotsBuilt < maxSlots) {
    // Skip Sunday (0)
    if (cursor.getDay() === 0) {
      cursor.setDate(cursor.getDate() + 1);
      cursor.setHours(openHour, openMin, 0, 0);
      continue;
    }

    // Skip before open or after close
    const curHour = cursor.getHours();
    const curMin = cursor.getMinutes();
    const curTime = curHour * 60 + curMin;
    const openTime = openHour * 60 + openMin;
    const closeTime = closeHour * 60 + closeMin;

    if (curTime < openTime || curTime > closeTime) {
      if (curTime > closeTime) {
        cursor.setDate(cursor.getDate() + 1);
      }
      cursor.setHours(openHour, openMin, 0, 0);
      continue;
    }

    const h = String(cursor.getHours()).padStart(2, '0');
    const m = String(cursor.getMinutes()).padStart(2, '0');
    const value = `${h}:${m}`;  // HH:MM format for webhook

    const label = cursor.toLocaleString('en-US', {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit'
    });

    options.push(`<option value="${value}">${label}</option>`);
    slotsBuilt++;
    cursor.setMinutes(cursor.getMinutes() + 30);
  }

  sel.innerHTML = '<option value="">Select a time…</option><option value="ASAP">ASAP (approx 30 min)</option>' + options.join('');
}

// ── Form Submit ──────────────────────────────────────────────────────────────
async function handleSubmit(e) {
  e.preventDefault();

  const btn = document.getElementById('submit-btn');
  const errBox = document.getElementById('error-msg');
  const okBox  = document.getElementById('success-msg');

  if (errBox) errBox.style.display = 'none';
  if (okBox) okBox.style.display  = 'none';

  const { subtotal, tax, total, items } = calcTotals();

  if (items.length === 0) {
    if (errBox) {
      errBox.textContent = 'Please add at least one item to your order.';
      errBox.style.display = 'block';
    }
    return;
  }

  const name  = document.getElementById('customer-name')?.value.trim();
  const email = document.getElementById('customer-email')?.value.trim();
  let phone = document.getElementById('customer-phone')?.value.trim().replace(/\D/g, '');
  const pickup = document.getElementById('pickup-time')?.value;
  const notes = document.getElementById('special-instructions')?.value.trim();

  if (!name || !email || !phone || !pickup) {
    if (errBox) {
      errBox.textContent = 'Please fill in all required fields.';
      errBox.style.display = 'block';
    }
    return;
  }

  if (phone.length < 10) {
    if (errBox) {
      errBox.textContent = 'Please enter a valid 10-digit phone number.';
      errBox.style.display = 'block';
    }
    return;
  }

  // Build payload matching WEBHOOK-DOCS.md schema (dollars, snake_case)
  const payload = {
    customer_name: name,
    email: email,
    phone: phone,
    order_items: items.map(it => ({
      item_id: it.id,
      name: it.name,
      qty: it.quantity,
      price: it.price
    })),
    subtotal: subtotal,
    tax: tax,
    total: total,
    pickup_time: pickup,
    special_instructions: notes,
    source: 'web',
    timestamp: new Date().toISOString()
  };

  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Placing Order…';
  }

  try {
    const res = await fetch('https://utopia-api.systack.net/webhook/utopia-deli-html-order-v1', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    // Safe response parsing — check Content-Type first (CODY-015)
    let data;
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      data = await res.json();
    } else {
      const text = await res.text();
      data = { success: res.ok, message: text || (res.ok ? 'Order placed' : 'Server error') };
    }

    if (!res.ok || data.success === false || data.ok === false) {
      // Structured error from webhook
      const errorMsg = data.error?.message || data.error || data.message || `Server error (${res.status})`;
      const errorDetails = data.error?.details?.join('\n') || '';
      const errorAction = data.error?.action || '';
      const errorContact = data.error?.contact || 'Call us at (501) 274-6231';

      let fullError = errorMsg;
      if (errorDetails) fullError += '\n' + errorDetails;
      if (errorAction) fullError += '\n' + errorAction;
      fullError += '\n' + errorContact;

      throw new Error(fullError);
    }

    // Success — show payment link if available
    const paymentMsg = data.payment_link
      ? ` Complete payment: ${data.payment_link}`
      : '';
    if (okBox) {
      okBox.innerHTML = `✅ ${data.message || 'Order placed successfully!'}${paymentMsg}`;
      okBox.style.display = 'block';
    }

    // Reset cart and form
    cart = {};
    renderMenu();
    renderCart();
    e.target.reset();
    buildPickupOptions();

  } catch (err) {
    console.error('Order submit error:', err);
    if (errBox) {
      errBox.innerHTML = err.message.replace(/\n/g, '<br>');
      errBox.style.display = 'block';
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Place Order';
    }
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderMenu();
  renderCart();
  buildPickupOptions();
  const form = document.getElementById('order-form');
  if (form) form.addEventListener('submit', handleSubmit);
});
