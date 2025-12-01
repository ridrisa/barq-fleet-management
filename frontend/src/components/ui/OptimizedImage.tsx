import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/cn';

interface OptimizedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  lazy?: boolean;
  fallbackSrc?: string;
  aspectRatio?: string;
  objectFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
  blur?: boolean;
}

/**
 * Optimized Image component with lazy loading, blur-up effect, and error handling
 */
export function OptimizedImage({
  src,
  alt,
  lazy = true,
  fallbackSrc = '/placeholder.png',
  aspectRatio,
  objectFit = 'cover',
  blur = true,
  className,
  ...props
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(src);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    setCurrentSrc(src);
    setError(false);
    setIsLoaded(false);
  }, [src]);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!lazy || !imgRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              observer.unobserve(img);
            }
          }
        });
      },
      {
        rootMargin: '50px', // Start loading 50px before image enters viewport
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current);
      }
    };
  }, [lazy]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setError(true);
    if (fallbackSrc && currentSrc !== fallbackSrc) {
      setCurrentSrc(fallbackSrc);
    }
  };

  return (
    <div
      className={cn('relative overflow-hidden', className)}
      style={{
        aspectRatio: aspectRatio || 'auto',
      }}
    >
      <img
        ref={imgRef}
        src={lazy ? undefined : currentSrc}
        data-src={lazy ? currentSrc : undefined}
        alt={alt}
        loading={lazy ? 'lazy' : 'eager'}
        decoding="async"
        onLoad={handleLoad}
        onError={handleError}
        className={cn(
          'w-full h-full transition-all duration-300',
          objectFit && `object-${objectFit}`,
          !isLoaded && blur && 'blur-sm scale-105',
          isLoaded && 'blur-0 scale-100',
          error && 'opacity-50'
        )}
        {...props}
      />
      {!isLoaded && !error && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
    </div>
  );
}
