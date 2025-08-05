export interface Option {
  value: string
  label: string
  icon?: React.ComponentType<{ className?: string }>
  count?: number
}

export type FilterOperator = 'eq' | 'ne' | 'lt' | 'lte' | 'gt' | 'gte' | 'in' | 'contains' | 'startswith' | 'endswith' | 'iLike' | 'notILike' | 'isEmpty' | 'isNotEmpty' | 'isBetween' | 'isNotBetween' | 'isRelativeToToday' | 'inArray' | 'notInArray'

export type FilterVariant = 'text' | 'number' | 'select' | 'multiSelect' | 'date' | 'dateRange' | 'range' | 'boolean'

export interface ExtendedColumnFilter {
  id: string
  value: any
  operator?: FilterOperator
}