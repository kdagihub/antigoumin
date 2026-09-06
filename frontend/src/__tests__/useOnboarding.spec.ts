import { describe, expect, it, beforeEach } from 'vitest'

import {
  isTutorialCompleted,
  isWizardCompleted,
  markTutorialCompleted,
  markWizardCompleted,
  shouldShowTutorial,
  shouldShowWizard,
} from '@/composables/useOnboarding'

describe('useOnboarding storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('shows wizard before tutorial for new users', () => {
    expect(shouldShowWizard(42)).toBe(true)
    expect(shouldShowTutorial(42)).toBe(false)
  })

  it('shows tutorial after wizard completion', () => {
    markWizardCompleted(42)
    expect(shouldShowWizard(42)).toBe(false)
    expect(shouldShowTutorial(42)).toBe(true)
  })

  it('hides both after full completion', () => {
    markWizardCompleted(42)
    markTutorialCompleted(42)
    expect(isWizardCompleted(42)).toBe(true)
    expect(isTutorialCompleted(42)).toBe(true)
    expect(shouldShowTutorial(42)).toBe(false)
  })
})
