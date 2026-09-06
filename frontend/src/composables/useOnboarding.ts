const WIZARD_KEY_PREFIX = 'agm:onboarding:wizard:'
const TUTORIAL_KEY_PREFIX = 'agm:onboarding:tutorial:'

function storageKey(prefix: string, userId: number): string {
  return `${prefix}${userId}`
}

export function isWizardCompleted(userId: number): boolean {
  return localStorage.getItem(storageKey(WIZARD_KEY_PREFIX, userId)) === '1'
}

export function isTutorialCompleted(userId: number): boolean {
  return localStorage.getItem(storageKey(TUTORIAL_KEY_PREFIX, userId)) === '1'
}

export function markWizardCompleted(userId: number): void {
  localStorage.setItem(storageKey(WIZARD_KEY_PREFIX, userId), '1')
}

export function markTutorialCompleted(userId: number): void {
  localStorage.setItem(storageKey(TUTORIAL_KEY_PREFIX, userId), '1')
}

export function resetTutorial(userId: number): void {
  localStorage.removeItem(storageKey(TUTORIAL_KEY_PREFIX, userId))
}

export function shouldShowWizard(userId: number | undefined): boolean {
  if (!userId) return false
  return !isWizardCompleted(userId)
}

export function shouldShowTutorial(userId: number | undefined): boolean {
  if (!userId) return false
  return isWizardCompleted(userId) && !isTutorialCompleted(userId)
}

export function resolveTutorialTarget(targetId: string): HTMLElement | null {
  const mobile = document.querySelector<HTMLElement>(`[data-tutorial="${targetId}-mobile"]`)
  if (mobile && mobile.offsetParent !== null) {
    return mobile
  }
  const desktop = document.querySelector<HTMLElement>(`[data-tutorial="${targetId}-desktop"]`)
  if (desktop && desktop.offsetParent !== null) {
    return desktop
  }
  return document.querySelector<HTMLElement>(`[data-tutorial="${targetId}"]`)
}
