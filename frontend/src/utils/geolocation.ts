/**
 * Geolocation utility for capturing user's current position
 * Provides automatic location detection with fallback for manual input
 */

export interface GeolocationPosition {
  latitude: number
  longitude: number
  accuracy?: number
  altitude?: number | null
  altitudeAccuracy?: number | null
  heading?: number | null
  speed?: number | null
  timestamp: number
}

export interface GeolocationError {
  code: number
  message: string
  permissionDenied?: boolean
}

export type GeolocationResult =
  | { success: true; position: GeolocationPosition }
  | { success: false; error: GeolocationError }

/**
 * Check if geolocation is supported in the current browser
 */
export function isGeolocationSupported(): boolean {
  return 'geolocation' in navigator
}

/**
 * Get the user's current position
 * @param options - Geolocation options (timeout, maximumAge, enableHighAccuracy)
 * @returns Promise with position or error
 */
export function getCurrentPosition(
  options: PositionOptions = {}
): Promise<GeolocationResult> {
  return new Promise((resolve) => {
    if (!isGeolocationSupported()) {
      resolve({
        success: false,
        error: {
          code: 0,
          message: 'Geolocation is not supported by this browser',
          permissionDenied: false,
        },
      })
      return
    }

    const defaultOptions: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
      ...options,
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          success: true,
          position: {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            altitudeAccuracy: position.coords.altitudeAccuracy,
            heading: position.coords.heading,
            speed: position.coords.speed,
            timestamp: position.timestamp,
          },
        })
      },
      (error) => {
        resolve({
          success: false,
          error: {
            code: error.code,
            message: getGeolocationErrorMessage(error.code),
            permissionDenied: error.code === error.PERMISSION_DENIED,
          },
        })
      },
      defaultOptions
    )
  })
}

/**
 * Watch the user's position changes
 * @param callback - Function to call when position changes
 * @param options - Geolocation options
 * @returns Watch ID that can be used to stop watching
 */
export function watchPosition(
  callback: (result: GeolocationResult) => void,
  options: PositionOptions = {}
): number | null {
  if (!isGeolocationSupported()) {
    callback({
      success: false,
      error: {
        code: 0,
        message: 'Geolocation is not supported by this browser',
      },
    })
    return null
  }

  const defaultOptions: PositionOptions = {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0,
    ...options,
  }

  return navigator.geolocation.watchPosition(
    (position) => {
      callback({
        success: true,
        position: {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          altitude: position.coords.altitude,
          altitudeAccuracy: position.coords.altitudeAccuracy,
          heading: position.coords.heading,
          speed: position.coords.speed,
          timestamp: position.timestamp,
        },
      })
    },
    (error) => {
      callback({
        success: false,
        error: {
          code: error.code,
          message: getGeolocationErrorMessage(error.code),
          permissionDenied: error.code === error.PERMISSION_DENIED,
        },
      })
    },
    defaultOptions
  )
}

/**
 * Stop watching position changes
 * @param watchId - Watch ID returned by watchPosition
 */
export function clearWatch(watchId: number | null): void {
  if (watchId !== null && isGeolocationSupported()) {
    navigator.geolocation.clearWatch(watchId)
  }
}

/**
 * Get human-readable error message for geolocation error code
 */
function getGeolocationErrorMessage(code: number): string {
  switch (code) {
    case 1:
      return 'Location access denied. Please enable location permissions in your browser settings.'
    case 2:
      return 'Unable to determine your location. The position acquisition failed.'
    case 3:
      return 'Location request timed out. Please try again.'
    default:
      return 'An unknown error occurred while getting your location.'
  }
}

/**
 * Format position as a string for display
 */
export function formatPosition(position: GeolocationPosition): string {
  return `${position.latitude.toFixed(6)}, ${position.longitude.toFixed(6)}`
}

/**
 * Calculate distance between two coordinates (in meters)
 * Uses Haversine formula
 */
export function calculateDistance(
  pos1: GeolocationPosition,
  pos2: GeolocationPosition
): number {
  const R = 6371e3 // Earth's radius in meters
  const φ1 = (pos1.latitude * Math.PI) / 180
  const φ2 = (pos2.latitude * Math.PI) / 180
  const Δφ = ((pos2.latitude - pos1.latitude) * Math.PI) / 180
  const Δλ = ((pos2.longitude - pos1.longitude) * Math.PI) / 180

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return R * c
}

/**
 * Request location permission (for browsers that require explicit request)
 */
export async function requestLocationPermission(): Promise<boolean> {
  if (!isGeolocationSupported()) {
    return false
  }

  // Try to get position once to trigger permission prompt
  const result = await getCurrentPosition({ timeout: 5000 })
  return result.success
}

/**
 * React hook for using geolocation
 */
export function useGeolocation(options?: PositionOptions) {
  const [position, setPosition] = React.useState<GeolocationPosition | null>(null)
  const [error, setError] = React.useState<GeolocationError | null>(null)
  const [loading, setLoading] = React.useState(false)

  const getLocation = React.useCallback(async () => {
    setLoading(true)
    setError(null)

    const result = await getCurrentPosition(options)

    setLoading(false)

    if (result.success) {
      setPosition(result.position)
      setError(null)
      return result.position
    } else {
      setError(result.error)
      return null
    }
  }, [options])

  React.useEffect(() => {
    // Auto-get location on mount if desired
    // getLocation()
  }, [])

  return {
    position,
    error,
    loading,
    getLocation,
    isSupported: isGeolocationSupported(),
  }
}

// Import React for the hook
import React from 'react'

export default {
  getCurrentPosition,
  watchPosition,
  clearWatch,
  isGeolocationSupported,
  formatPosition,
  calculateDistance,
  requestLocationPermission,
  useGeolocation,
}
