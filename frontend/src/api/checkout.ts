import { createCheckout, type CheckoutPayload } from '@/api/payments'

export async function redirectToGeniusPay(payload: CheckoutPayload): Promise<void> {
  const session = await createCheckout(payload)
  window.location.assign(session.checkout_url)
}
