import config from '../config.js';

// Demo data for when backend is not available
const DEMO_EBAY_RESULTS = [
  {
    itemId: 'demo1',
    title: 'Vintage Leather Jacket - Brown',
    price: { value: '89.99', currency: 'USD' },
    image: { imageUrl: 'https://via.placeholder.com/300x300/8B5CF6/white?text=Leather+Jacket' },
    seller: { username: 'vintagestyle' },
    itemWebUrl: 'https://www.ebay.com',
    itemAffiliateWebUrl: 'https://www.ebay.com'
  },
  {
    itemId: 'demo2',
    title: 'Nike Air Max Sneakers - Size 10',
    price: { value: '129.99', currency: 'USD' },
    image: { imageUrl: 'https://via.placeholder.com/300x300/FF9800/white?text=Nike+Sneakers' },
    seller: { username: 'sneakerstore' },
    itemWebUrl: 'https://www.ebay.com',
    itemAffiliateWebUrl: 'https://www.ebay.com'
  },
  {
    itemId: 'demo3',
    title: 'Vintage Band T-Shirt - The Beatles',
    price: { value: '45.00', currency: 'USD' },
    image: { imageUrl: 'https://via.placeholder.com/300x300/4CAF50/white?text=Band+Tee' },
    seller: { username: 'musicmerchandise' },
    itemWebUrl: 'https://www.ebay.com',
    itemAffiliateWebUrl: 'https://www.ebay.com'
  },
  {
    itemId: 'demo4',
    title: 'Designer Handbag - Louis Vuitton Style',
    price: { value: '199.99', currency: 'USD' },
    image: { imageUrl: 'https://via.placeholder.com/300x300/E91E63/white?text=Handbag' },
    seller: { username: 'luxurygoods' },
    itemWebUrl: 'https://www.ebay.com',
    itemAffiliateWebUrl: 'https://www.ebay.com'
  },
  {
    itemId: 'demo5',
    title: 'Vintage Denim Jeans - High Waisted',
    price: { value: '69.99', currency: 'USD' },
    image: { imageUrl: 'https://via.placeholder.com/300x300/2196F3/white?text=Denim+Jeans' },
    seller: { username: 'denimcollection' },
    itemWebUrl: 'https://www.ebay.com',
    itemAffiliateWebUrl: 'https://www.ebay.com'
  }
];

const DEMO_PRICE_ANALYSIS = {
  suggested_price: 89.99,
  price_range_low: 69.99,
  price_range_high: 109.99,
  confidence_score: 'High (Demo Mode)',
  analysis: 'Demo mode: This is simulated price analysis data.'
};

const DEMO_SYSTEM_STATUS = {
  backend: true,
  database: true,
  redis: true,
  celery: true,
  ebay_tokens: true,
  ai_services: {
    vision: true,
    rekognition: true,
    gemini: true,
    vertex: true
  }
};

const DEMO_PERFORMANCE_METRICS = {
  total_searches: 1234,
  successful_searches: 1180,
  average_response_time: 1.2,
  ai_confidence_avg: 89.5
};

const DEMO_IMAGE_ANALYSIS = {
  analysis_results: {
    visually_ranked_comps: DEMO_EBAY_RESULTS,
    analysis: {
      detected_items: ['clothing', 'fashion'],
      confidence: 0.95,
      dominant_colors: ['#8B5CF6', '#000000'],
      style: 'vintage'
    }
  },
  queries: {
    primary: 'vintage clothing fashion',
    variants: [
      { query: 'vintage clothing', confidence: 0.95 },
      { query: 'retro fashion', confidence: 0.88 },
      { query: 'classic style', confidence: 0.82 }
    ]
  }
};

export const DemoDataService = {
  isEnabled: () => config.DEMO_MODE,
  
  getEbaySearchResults: (query) => {
    // Filter results based on query for more realistic behavior
    const filtered = DEMO_EBAY_RESULTS.filter(item => 
      item.title.toLowerCase().includes(query.toLowerCase().split(' ')[0]) ||
      query.toLowerCase().includes('demo') ||
      query.length < 3
    );
    return filtered.length > 0 ? filtered : DEMO_EBAY_RESULTS.slice(0, 3);
  },
  
  getPriceAnalysis: (query) => ({
    ...DEMO_PRICE_ANALYSIS,
    title: query
  }),
  
  getSystemStatus: () => DEMO_SYSTEM_STATUS,
  
  getPerformanceMetrics: () => DEMO_PERFORMANCE_METRICS,
  
  getImageAnalysis: () => DEMO_IMAGE_ANALYSIS,
  
  delay: (ms = 1000) => new Promise(resolve => setTimeout(resolve, ms))
};

export default DemoDataService;