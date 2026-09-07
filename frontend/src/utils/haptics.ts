/**
 * Haptic vibration feedback utility for mobile touch interactions.
 * Works with HTML5 Vibration API on Chrome / Android (vivo X300 Pro)
 * and safely no-ops on desktop / unsupported devices.
 */
export const haptics = {
  // Crisp short click (12ms)
  click() {
    try {
      if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
        navigator.vibrate(12)
      }
    } catch (e) {
      // ignore
    }
  },

  // Soft single buzz for correct answer (25ms)
  correct() {
    try {
      if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
        navigator.vibrate(25)
      }
    } catch (e) {
      // ignore
    }
  },

  // Double buzz for incorrect answer (50ms - pause 40ms - 50ms)
  wrong() {
    try {
      if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
        navigator.vibrate([45, 35, 45])
      }
    } catch (e) {
      // ignore
    }
  },

  // Noticeable buzz for completing exam or milestone
  milestone() {
    try {
      if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
        navigator.vibrate([60, 50, 100])
      }
    } catch (e) {
      // ignore
    }
  },

  // Soft selection feedback
  selection() {
    try {
      if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
        navigator.vibrate(15)
      }
    } catch (e) {
      // ignore
    }
  },

  // Heavy action feedback (e.g. deletion or reset)
  heavy() {
    try {
      if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
        navigator.vibrate([30, 40, 30])
      }
    } catch (e) {
      // ignore
    }
  }
}
