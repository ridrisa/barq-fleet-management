import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useForm, ValidationSchema } from '../useForm'

describe('useForm', () => {
  interface TestFormData {
    name: string
    email: string
    age: number
  }

  const initialData: TestFormData = {
    name: '',
    email: '',
    age: 0,
  }

  const validationSchema: ValidationSchema<TestFormData> = {
    name: (data) => (!data.name ? 'Name is required' : null),
    email: (data) => (!data.email ? 'Email is required' : null),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with provided data', () => {
    const onSubmit = vi.fn()

    const { result } = renderHook(() =>
      useForm({
        initialData,
        validationSchema,
        onSubmit,
      })
    )

    expect(result.current.formData).toEqual(initialData)
    expect(result.current.errors).toEqual({})
    expect(result.current.isLoading).toBe(false)
  })

  it('should update form data on handleChange', () => {
    const onSubmit = vi.fn()

    const { result } = renderHook(() =>
      useForm({
        initialData,
        validationSchema,
        onSubmit,
      })
    )

    act(() => {
      result.current.handleChange('name', 'John Doe')
    })

    expect(result.current.formData.name).toBe('John Doe')
  })

  it('should clear error when field is changed', () => {
    const onSubmit = vi.fn()

    const { result } = renderHook(() =>
      useForm({
        initialData,
        validationSchema,
        onSubmit,
      })
    )

    // First, trigger validation to create errors
    const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

    act(() => {
      result.current.handleSubmit(mockEvent)
    })

    // Should have name error
    expect(result.current.errors.name).toBe('Name is required')

    // Now change the name field
    act(() => {
      result.current.handleChange('name', 'John')
    })

    // Error should be cleared
    expect(result.current.errors.name).toBeUndefined()
  })

  it('should not submit if validation fails', async () => {
    const onSubmit = vi.fn()

    const { result } = renderHook(() =>
      useForm({
        initialData,
        validationSchema,
        onSubmit,
      })
    )

    const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

    act(() => {
      result.current.handleSubmit(mockEvent)
    })

    expect(result.current.errors.name).toBe('Name is required')
    expect(result.current.errors.email).toBe('Email is required')
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('should submit if validation passes', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)

    const { result } = renderHook(() =>
      useForm({
        initialData: { name: 'John', email: 'john@example.com', age: 25 },
        validationSchema,
        onSubmit,
      })
    )

    const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    expect(onSubmit).toHaveBeenCalledWith({
      name: 'John',
      email: 'john@example.com',
      age: 25,
    })
  })

  it('should set isLoading during submission', async () => {
    let resolveSubmit: () => void
    const onSubmit = vi.fn().mockImplementation(
      () => new Promise<void>((resolve) => {
        resolveSubmit = resolve
      })
    )

    const { result } = renderHook(() =>
      useForm({
        initialData: { name: 'John', email: 'john@example.com', age: 25 },
        validationSchema,
        onSubmit,
      })
    )

    const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

    act(() => {
      result.current.handleSubmit(mockEvent)
    })

    expect(result.current.isLoading).toBe(true)

    await act(async () => {
      resolveSubmit!()
    })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
  })

  it('should handle submission error gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const onSubmit = vi.fn().mockRejectedValue(new Error('Submission failed'))

    const { result } = renderHook(() =>
      useForm({
        initialData: { name: 'John', email: 'john@example.com', age: 25 },
        validationSchema,
        onSubmit,
      })
    )

    const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    expect(result.current.isLoading).toBe(false)
    expect(consoleErrorSpy).toHaveBeenCalled()

    consoleErrorSpy.mockRestore()
  })

  it('should prevent default form submission', async () => {
    const onSubmit = vi.fn()

    const { result } = renderHook(() =>
      useForm({
        initialData,
        validationSchema,
        onSubmit,
      })
    )

    const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

    act(() => {
      result.current.handleSubmit(mockEvent)
    })

    expect(mockEvent.preventDefault).toHaveBeenCalled()
  })

  it('should handle multiple field changes', () => {
    const onSubmit = vi.fn()

    const { result } = renderHook(() =>
      useForm({
        initialData,
        validationSchema,
        onSubmit,
      })
    )

    act(() => {
      result.current.handleChange('name', 'John Doe')
      result.current.handleChange('email', 'john@example.com')
      result.current.handleChange('age', 30)
    })

    expect(result.current.formData).toEqual({
      name: 'John Doe',
      email: 'john@example.com',
      age: 30,
    })
  })

  it('should work with empty validation schema', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)

    const { result } = renderHook(() =>
      useForm({
        initialData,
        validationSchema: {},
        onSubmit,
      })
    )

    const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    expect(onSubmit).toHaveBeenCalled()
  })
})
