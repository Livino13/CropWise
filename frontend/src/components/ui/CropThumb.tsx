import React, { useState } from 'react'
import { cropPhoto, cropEmoji } from '@/utils/cropMeta'

export function CropThumb({ crop, className = 'w-8 h-8', rounded = 'rounded-lg' }: { crop?: string; className?: string; rounded?: string }) {
  const [failed, setFailed] = useState(false)
  const photo = crop ? cropPhoto(crop) : null
  const showPhoto = photo && !failed
  return (
    <span className={`inline-grid place-items-center overflow-hidden border border-stone-200 bg-stone-100 ${rounded} ${className}`}>
      {showPhoto ? (
        <img src={photo!} alt={crop || ''} loading="lazy" onError={() => setFailed(true)} className="w-full h-full object-cover" />
      ) : (
        <span className="text-lg leading-none">{cropEmoji(crop || '')}</span>
      )}
    </span>
  )
}

export default CropThumb
