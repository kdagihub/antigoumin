const IVORY_COAST_CODE = '225'
const LOCAL_LENGTH = 10

export function digitsOnly(value: string): string {
  return value.replace(/\D/g, '')
}

/** Retire l'indicatif 225 pour n'afficher que le numéro local. */
export function toIvorianLocalDigits(value: string): string {
  const digits = digitsOnly(value)
  if (digits.startsWith(IVORY_COAST_CODE) && digits.length > LOCAL_LENGTH) {
    return digits.slice(IVORY_COAST_CODE.length)
  }
  return digits
}

/** Formate un numéro local ivoirien pour l'affichage (07 00 00 00 00). */
export function formatIvorianLocalDisplay(value: string): string {
  const digits = toIvorianLocalDigits(value).slice(0, LOCAL_LENGTH)
  const parts: string[] = []
  for (let i = 0; i < digits.length; i += 2) {
    parts.push(digits.slice(i, i + 2))
  }
  return parts.join(' ')
}

/** Valeur envoyée à l'API (chiffres locaux, sans indicatif). */
export function normalizeIvorianPhoneForApi(localValue: string): string {
  return toIvorianLocalDigits(localValue)
}

export function isValidIvorianLocalPhone(value: string): boolean {
  const digits = toIvorianLocalDigits(value)
  return digits.length === LOCAL_LENGTH && digits.startsWith('0')
}
