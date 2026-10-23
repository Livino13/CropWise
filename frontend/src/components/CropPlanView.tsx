import type { CropPlan } from '@/api/types'

function fmt(value: number) {
  return Number.isInteger(value) ? value.toFixed(0) : value.toFixed(1)
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[68px_1fr] gap-2 text-xs leading-relaxed">
      <div className="font-semibold text-stone-700">{label}</div>
      <div className="text-stone-600">{children}</div>
    </div>
  )
}

export function CropPlanView({
  plan,
  onExplain,
  explaining = false,
}: {
  plan: CropPlan
  onExplain?: () => void
  explaining?: boolean
}) {
  const g = plan.growing
  const f = plan.fertilizer
  const perPlant = f.unit !== 'kg/ha'
  const scope = plan.field?.name
    ? `For ${plan.field.name}`
    : plan.basis.personalized || plan.personalized
      ? 'Based on your inputs'
      : 'Standard plan'

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[11px] font-semibold text-brand-800 bg-brand-50 border border-brand-200 rounded-full px-2.5 py-0.5">
          {scope}
        </span>
        {plan.basis.weather?.includes('Open-Meteo') && (
          <span className="text-[10px] text-stone-500">Weather forecast included</span>
        )}
      </div>

      <section>
        <h3 className="text-sm font-semibold text-stone-800">Growing plan</h3>
        <div className="mt-1.5 space-y-2">
          <Row label="Sowing">{g.sowing}</Row>
          <Row label="Water">{g.irrigation}</Row>
          <Row label="Harvest">{g.harvest}</Row>
          <Row label="Soil prep">{g.soil_prep}</Row>
        </div>
      </section>

      {g.risks.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
          <div className="text-xs font-semibold text-amber-800">Watch out</div>
          <ul className="mt-1 list-disc list-inside space-y-0.5 text-[11px] text-amber-800">
            {g.risks.map((risk, i) => <li key={i}>{risk}</li>)}
          </ul>
        </div>
      )}

      <section>
        <h3 className="text-sm font-semibold text-stone-800">Fertilizer plan</h3>

        {perPlant ? (
          <p className="mt-1 text-xs text-stone-600">
            Dose unit: <span className="font-medium">{f.unit}</span>. Follow the reference timing below and
            confirm the per-plant dose with your local agriculture officer.
          </p>
        ) : f.personalized && f.available && f.deficit ? (
          <div className="mt-1.5 rounded-lg border border-brand-200 bg-brand-50 p-3">
            <div className="text-xs font-semibold text-brand-900">Your soil deficit</div>
            <div className="mt-0.5 text-sm font-bold text-brand-900 tabular-nums">
              N {fmt(f.deficit.n)} · P {fmt(f.deficit.p)} · K {fmt(f.deficit.k)}{' '}
              <span className="text-xs font-normal">kg/ha</span>
            </div>
            <div className="mt-1 text-[10px] text-brand-800">
              Soil test: N {fmt(f.available.n)} · P {fmt(f.available.p)} · K {fmt(f.available.k)} kg/ha
              {f.target && <> · Crop target: N {fmt(f.target.n)} · P {fmt(f.target.p)} · K {fmt(f.target.k)}</>}
            </div>
          </div>
        ) : (
          <div className="mt-1.5 rounded-lg border border-stone-200 bg-stone-50 p-3">
            <div className="text-xs font-semibold text-stone-700">Standard crop dose</div>
            <div className="mt-0.5 text-[11px] text-stone-500">
              This dose is not adjusted to your soil. Select a field with a soil test, or add N/P/K values,
              to get a field-specific deficit.
            </div>
          </div>
        )}

        {f.products.length > 0 && (
          <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
            {f.products.map((p) => (
              <div key={p.name} className="rounded-lg border border-stone-200 bg-white p-2.5">
                <div className="text-[11px] font-semibold text-stone-700">{p.name}</div>
                <div className="mt-0.5 text-base font-bold text-stone-900 tabular-nums">
                  {fmt(p.kg_per_ha)} <span className="text-[10px] font-normal text-stone-500">kg/ha</span>
                </div>
                <div className="text-[10px] text-stone-500 tabular-nums">
                  {fmt(p.kg_per_acre)} kg/acre · {p.bags_per_acre.toFixed(2)} bags/acre
                </div>
              </div>
            ))}
          </div>
        )}

        {f.stages.length > 0 && (
          <div className="mt-3">
            <div className="text-xs font-semibold text-stone-700">Timing</div>
            <ul className="mt-1.5 space-y-2">
              {f.stages.map((stage, i) => {
                const amounts = [
                  stage.dap_kg != null && stage.dap_kg > 0 ? `DAP ${fmt(stage.dap_kg)} kg/ha` : null,
                  stage.mop_kg != null && stage.mop_kg > 0 ? `MOP ${fmt(stage.mop_kg)} kg/ha` : null,
                  stage.urea_kg != null && stage.urea_kg > 0 ? `Urea ${fmt(stage.urea_kg)} kg/ha` : null,
                ].filter(Boolean)
                return (
                  <li key={`${stage.stage}-${i}`} className="border-l-2 border-brand-200 pl-2 text-xs">
                    <div className="font-medium text-stone-800">
                      {stage.stage} <span className="font-normal text-stone-400">({stage.share})</span>
                    </div>
                    <div className="text-stone-600">{stage.products}</div>
                    {amounts.length > 0 && (
                      <div className="mt-0.5 font-medium text-brand-700">{amounts.join(' · ')}</div>
                    )}
                  </li>
                )
              })}
            </ul>
          </div>
        )}

        {f.ph_advice && (
          <div className="mt-2 rounded-lg bg-amber-50 px-2.5 py-2 text-[11px] text-amber-800">{f.ph_advice}</div>
        )}
        {f.notes.length > 0 && (
          <ul className="mt-2 space-y-1 text-[10px] leading-relaxed text-stone-500">
            {f.notes.map((note, i) => <li key={i}>{note}</li>)}
          </ul>
        )}
      </section>

      {plan.pests.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-stone-800">Pests to watch</h3>
          <ul className="mt-1.5 space-y-2">
            {plan.pests.map((pest, i) => (
              <li key={`${pest.pest}-${i}`} className="border-l-2 border-stone-200 pl-2 text-xs">
                <div className="font-medium capitalize text-stone-800">{pest.pest}</div>
                <div className="text-stone-600">Chemical: {pest.treatment}</div>
                <div className="text-emerald-700">Organic: {pest.organic}</div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {plan.ai_explanation ? (
        <div className="rounded-lg border border-brand-200 bg-brand-50 p-3">
          <div className="text-xs font-semibold text-brand-900">CropWise explains</div>
          <div className="mt-1 whitespace-pre-wrap text-xs leading-relaxed text-brand-900">
            {plan.ai_explanation}
          </div>
        </div>
      ) : onExplain ? (
        <button
          type="button"
          onClick={onExplain}
          disabled={explaining}
          className="text-xs font-semibold text-brand-700 hover:text-brand-800 disabled:opacity-50"
        >
          {explaining ? 'Writing a simple explanation…' : 'Explain this plan in simple words →'}
        </button>
      ) : null}

      <p className="text-[10px] text-stone-400">
        Data: {plan.basis.weather ?? 'No live weather'} · {plan.basis.soil ?? 'standard crop targets'}.
        {' '}Confirm fertilizer grades and pesticide doses with your local dealer or agriculture officer.
      </p>
    </div>
  )
}
