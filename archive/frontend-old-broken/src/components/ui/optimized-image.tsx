import Image from 'next/image'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { logger } from '@/lib/logfire'

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  priority?: boolean
  className?: string
  fill?: boolean
  sizes?: string
  quality?: number
  placeholder?: 'blur' | 'empty'
  blurDataURL?: string
  onLoadingComplete?: () => void
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className,
  fill = false,
  sizes,
  quality = 75,
  placeholder = 'blur',
  blurDataURL,
  onLoadingComplete,
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  const handleLoadingComplete = () => {
    setIsLoading(false)
    logger.info('Image loaded', { src, alt })
    onLoadingComplete?.()
  }

  const handleError = () => {
    setHasError(true)
    setIsLoading(false)
    logger.error('Image failed to load', new Error('Image load error'), { src, alt })
  }

  // Generate blur placeholder for optimization
  const defaultBlurDataURL = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='

  if (hasError) {
    return (
      <div 
        className={cn(
          'bg-zinc-800 flex items-center justify-center',
          className,
          fill && 'absolute inset-0'
        )}
        style={!fill ? { width, height } : undefined}
      >
        <span className="text-zinc-500 text-xs">Failed to load image</span>
      </div>
    )
  }

  return (
    <div className={cn('relative', className)}>
      {isLoading && (
        <div 
          className={cn(
            'absolute inset-0 bg-zinc-800 animate-pulse',
            'flex items-center justify-center'
          )}
        >
          <div className="w-8 h-8 border-2 border-zinc-600 border-t-zinc-400 rounded-full animate-spin" />
        </div>
      )}
      
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        fill={fill}
        sizes={sizes || (fill ? '100vw' : undefined)}
        priority={priority}
        quality={quality}
        placeholder={placeholder}
        blurDataURL={blurDataURL || defaultBlurDataURL}
        className={cn(
          'transition-opacity duration-300',
          isLoading ? 'opacity-0' : 'opacity-100'
        )}
        onLoadingComplete={handleLoadingComplete}
        onError={handleError}
      />
    </div>
  )
}

// Avatar component with optimization
export function OptimizedAvatar({
  src,
  alt,
  size = 40,
  className,
}: {
  src?: string
  alt: string
  size?: number
  className?: string
}) {
  const initials = alt
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  if (!src) {
    return (
      <div
        className={cn(
          'flex items-center justify-center bg-zinc-700 text-zinc-300 font-medium rounded-full',
          className
        )}
        style={{ width: size, height: size, fontSize: size * 0.4 }}
      >
        {initials}
      </div>
    )
  }

  return (
    <OptimizedImage
      src={src}
      alt={alt}
      width={size}
      height={size}
      className={cn('rounded-full overflow-hidden', className)}
      priority={false}
    />
  )
}