export function formatDate(s: string){ return new Date(s).toLocaleDateString('en-IN',{year:'numeric',month:'short',day:'numeric'}) }
export function confidenceColor(v:number){
  if(v>=0.7) return 'text-green-600 bg-green-50 border-green-200'
  if(v>=0.4) return 'text-amber-600 bg-amber-50 border-amber-200'
  return 'text-stone-500 bg-stone-50 border-stone-200'
}
export function confidenceLabel(v:number){
  if(v>=0.7) return 'Excellent match'
  if(v>=0.4) return 'Good match'
  return 'Moderate'
}
