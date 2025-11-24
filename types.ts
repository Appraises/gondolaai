export interface PromotionSuggestion {
  title: string;
  strategy: string;
  discount: string;
  reasoning: string;
}

export interface ProductDemoData {
  name: string;
  daysUntilExpiry: number;
  currentStock: number;
  price: number;
}

export enum AnalysisStatus {
  IDLE = 'IDLE',
  ANALYZING = 'ANALYZING',
  COMPLETE = 'COMPLETE',
  ERROR = 'ERROR'
}