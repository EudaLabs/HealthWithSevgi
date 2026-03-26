declare module 'plotly.js-basic-dist-min' {
  import Plotly from 'plotly.js'
  export default Plotly
}

declare module 'react-plotly.js/factory' {
  import type { ComponentType } from 'react'
  function createPlotlyComponent(plotly: unknown): ComponentType<Record<string, unknown>>
  export default createPlotlyComponent
}

declare module '@nivo/radar' {
  import type { ComponentType } from 'react'
  export const ResponsiveRadar: ComponentType<Record<string, unknown>>
}

