import { Disclosure } from '@headlessui/react'
export function Accordion({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Disclosure>
      {({ open }) => (
        <div className="border border-stone-200 rounded-lg overflow-hidden">
          <Disclosure.Button className="flex w-full justify-between items-center px-4 py-3 text-sm font-medium bg-stone-50 hover:bg-stone-100">
            <span>{title}</span><span className={`transition-transform ${open?'rotate-180':''}`}>▾</span>
          </Disclosure.Button>
          <Disclosure.Panel className="px-4 py-3 text-sm text-stone-600 bg-white">{children}</Disclosure.Panel>
        </div>
      )}
    </Disclosure>
  )
}
