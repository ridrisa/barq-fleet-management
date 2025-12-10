import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import {
  useMobile,
  useBreakpoint,
  useTouchDevice,
  useSafeAreaInsets,
  useLockBodyScroll,
  useKeyboardVisible,
  BREAKPOINTS,
} from '../useMobile'

describe('useMobile', () => {
  const originalInnerWidth = window.innerWidth

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    })
  })

  it('should return true when viewport is below breakpoint', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 500,
    })

    const { result } = renderHook(() => useMobile('md'))

    expect(result.current).toBe(true)
  })

  it('should return false when viewport is above breakpoint', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1200,
    })

    const { result } = renderHook(() => useMobile('md'))

    expect(result.current).toBe(false)
  })

  it('should use default breakpoint (md) when none specified', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 600,
    })

    const { result } = renderHook(() => useMobile())

    expect(result.current).toBe(true)
  })

  it('should update on resize event', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1200,
    })

    const { result } = renderHook(() => useMobile('md'))

    expect(result.current).toBe(false)

    act(() => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 500,
      })
      window.dispatchEvent(new Event('resize'))
    })

    expect(result.current).toBe(true)
  })

  it('should work with different breakpoints', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 700,
    })

    const { result: smResult } = renderHook(() => useMobile('sm'))
    const { result: lgResult } = renderHook(() => useMobile('lg'))

    expect(smResult.current).toBe(false) // 700 > 640
    expect(lgResult.current).toBe(true) // 700 < 1024
  })
})

describe('useBreakpoint', () => {
  const originalInnerWidth = window.innerWidth

  afterEach(() => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    })
  })

  it('should return xs for very small screens', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 300,
    })

    const { result } = renderHook(() => useBreakpoint())

    expect(result.current).toBe('xs')
  })

  it('should return sm for small screens', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 650,
    })

    const { result } = renderHook(() => useBreakpoint())

    expect(result.current).toBe('sm')
  })

  it('should return md for medium screens', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 900,
    })

    const { result } = renderHook(() => useBreakpoint())

    expect(result.current).toBe('md')
  })

  it('should return lg for large screens', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1100,
    })

    const { result } = renderHook(() => useBreakpoint())

    expect(result.current).toBe('lg')
  })

  it('should return xl for extra large screens', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1400,
    })

    const { result } = renderHook(() => useBreakpoint())

    expect(result.current).toBe('xl')
  })

  it('should return 2xl for very large screens', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1600,
    })

    const { result } = renderHook(() => useBreakpoint())

    expect(result.current).toBe('2xl')
  })
})

describe('useTouchDevice', () => {
  const originalOntouchstart = window.ontouchstart
  const originalMaxTouchPoints = navigator.maxTouchPoints

  afterEach(() => {
    // Reset touch properties
    Object.defineProperty(window, 'ontouchstart', {
      writable: true,
      configurable: true,
      value: originalOntouchstart,
    })
    Object.defineProperty(navigator, 'maxTouchPoints', {
      writable: true,
      configurable: true,
      value: originalMaxTouchPoints,
    })
  })

  it('should return false for non-touch devices', () => {
    Object.defineProperty(window, 'ontouchstart', {
      writable: true,
      configurable: true,
      value: undefined,
    })
    Object.defineProperty(navigator, 'maxTouchPoints', {
      writable: true,
      configurable: true,
      value: 0,
    })

    const { result } = renderHook(() => useTouchDevice())

    expect(result.current).toBe(false)
  })

  it('should return true when ontouchstart is present', () => {
    Object.defineProperty(window, 'ontouchstart', {
      writable: true,
      configurable: true,
      value: () => {},
    })

    const { result } = renderHook(() => useTouchDevice())

    expect(result.current).toBe(true)
  })

  it('should return true when maxTouchPoints > 0', () => {
    Object.defineProperty(navigator, 'maxTouchPoints', {
      writable: true,
      configurable: true,
      value: 5,
    })

    const { result } = renderHook(() => useTouchDevice())

    expect(result.current).toBe(true)
  })
})

describe('useSafeAreaInsets', () => {
  it('should return default inset values', () => {
    const { result } = renderHook(() => useSafeAreaInsets())

    expect(result.current).toEqual({
      top: 0,
      bottom: 0,
      left: 0,
      right: 0,
    })
  })
})

describe('useLockBodyScroll', () => {
  const originalOverflow = document.body.style.overflow

  afterEach(() => {
    document.body.style.overflow = originalOverflow
  })

  it('should lock body scroll when isLocked is true', () => {
    const { rerender } = renderHook(({ isLocked }) => useLockBodyScroll(isLocked), {
      initialProps: { isLocked: true },
    })

    expect(document.body.style.overflow).toBe('hidden')

    rerender({ isLocked: false })
  })

  it('should not lock body scroll when isLocked is false', () => {
    renderHook(({ isLocked }) => useLockBodyScroll(isLocked), {
      initialProps: { isLocked: false },
    })

    expect(document.body.style.overflow).not.toBe('hidden')
  })

  it('should restore original overflow on unmount', () => {
    document.body.style.overflow = 'auto'

    const { unmount } = renderHook(({ isLocked }) => useLockBodyScroll(isLocked), {
      initialProps: { isLocked: true },
    })

    expect(document.body.style.overflow).toBe('hidden')

    unmount()

    expect(document.body.style.overflow).toBe('auto')
  })
})

describe('useKeyboardVisible', () => {
  it('should return false by default', () => {
    const { result } = renderHook(() => useKeyboardVisible())

    expect(result.current).toBe(false)
  })
})

describe('BREAKPOINTS', () => {
  it('should have correct breakpoint values', () => {
    expect(BREAKPOINTS.xs).toBe(320)
    expect(BREAKPOINTS.sm).toBe(640)
    expect(BREAKPOINTS.md).toBe(768)
    expect(BREAKPOINTS.lg).toBe(1024)
    expect(BREAKPOINTS.xl).toBe(1280)
    expect(BREAKPOINTS['2xl']).toBe(1536)
  })
})
