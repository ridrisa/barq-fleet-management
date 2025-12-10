import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import {
  Truck, Users, BarChart3, Shield, Clock, Globe,
  CheckCircle, ArrowRight, Menu, X, Star,
  Building2, Wallet, MapPin, Headphones, Zap, Award,
  Play, ChevronDown, ChevronUp, Smartphone,
  Package, Route, FileText, Settings, Bell, Lock,
  TrendingUp, Calendar, CreditCard, UserCheck,
  CircleDot, Activity, Database, Cloud,
  Phone, Mail, MessageCircle
} from 'lucide-react'

// Animation hook for scroll reveal
function useScrollAnimation() {
  const ref = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [])

  return { ref, isVisible }
}

const features = [
  {
    icon: Truck,
    title: 'Fleet Management',
    description: 'Complete vehicle lifecycle management from acquisition to retirement. Track maintenance, fuel, assignments, and real-time location.',
    color: 'bg-blue-500',
    details: ['Vehicle tracking', 'Maintenance scheduling', 'Fuel monitoring', 'Document management']
  },
  {
    icon: Users,
    title: 'Courier Operations',
    description: 'Manage your entire delivery workforce. Handle onboarding, assignments, performance tracking, and payroll seamlessly.',
    color: 'bg-green-500',
    details: ['Performance analytics', 'Route assignment', 'Attendance tracking', 'Mobile app']
  },
  {
    icon: Wallet,
    title: 'HR & Finance',
    description: 'Integrated salary processing, leave management, loans, accommodations, and COD reconciliation all in one place.',
    color: 'bg-purple-500',
    details: ['Payroll automation', 'Leave management', 'Expense tracking', 'COD reconciliation']
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Real-time dashboards, KPI tracking, custom reports, and AI-powered forecasting to drive data-driven decisions.',
    color: 'bg-orange-500',
    details: ['Custom dashboards', 'Export reports', 'Trend analysis', 'AI predictions']
  },
  {
    icon: MapPin,
    title: 'Route Optimization',
    description: 'Smart delivery routing, zone management, dispatch automation, and real-time tracking for maximum efficiency.',
    color: 'bg-red-500',
    details: ['Auto-dispatch', 'Zone management', 'Live tracking', 'ETA predictions']
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'Bank-grade encryption, role-based access, audit logging, and compliance with industry standards.',
    color: 'bg-indigo-500',
    details: ['RBAC controls', 'Audit logging', 'Data encryption', 'SSO support']
  }
]

const stats = [
  { value: '99.9%', label: 'Uptime SLA' },
  { value: '50%', label: 'Cost Reduction' },
  { value: '3x', label: 'Faster Operations' },
  { value: '10K+', label: 'Vehicles Managed' }
]

const testimonials = [
  {
    quote: "SYNC transformed our logistics operations. We reduced delivery times by 40% and cut operational costs significantly.",
    author: "Ahmed Al-Rashid",
    role: "Operations Director",
    company: "FastTrack Logistics",
    rating: 5,
    image: null
  },
  {
    quote: "The HR and Finance integration alone saved us countless hours. Everything is now automated and accurate.",
    author: "Sarah Martinez",
    role: "CFO",
    company: "Express Delivery Co.",
    rating: 5,
    image: null
  },
  {
    quote: "Best fleet management solution we've used. The real-time tracking and analytics are game-changers.",
    author: "Mohammed Hassan",
    role: "Fleet Manager",
    company: "Gulf Transport Services",
    rating: 5,
    image: null
  }
]

const pricingPlans = [
  {
    name: 'Starter',
    price: '2,499',
    period: '/month',
    description: 'Perfect for small fleets getting started',
    features: [
      'Up to 50 vehicles',
      'Up to 100 couriers',
      'Basic analytics',
      'Email support',
      'Mobile app access'
    ],
    cta: 'Start Free Trial',
    popular: false
  },
  {
    name: 'Professional',
    price: '7,999',
    period: '/month',
    description: 'For growing logistics operations',
    features: [
      'Up to 250 vehicles',
      'Up to 500 couriers',
      'Advanced analytics & forecasting',
      'Priority support',
      'Custom integrations',
      'White-label options'
    ],
    cta: 'Start Free Trial',
    popular: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For large-scale fleet operations',
    features: [
      'Unlimited vehicles',
      'Unlimited couriers',
      'Custom AI models',
      'Dedicated support team',
      'On-premise deployment option',
      'SLA guarantees',
      'Custom development'
    ],
    cta: 'Contact Sales',
    popular: false
  }
]

// Platform integrations (coming soon)
const integrations: Array<{ name: string; logo: string; description: string }> = []

const faqs = [
  {
    question: 'How long does it take to set up SYNC?',
    answer: 'Most businesses are up and running within 24-48 hours. Our onboarding team will help you import your existing data and train your team on the platform.'
  },
  {
    question: 'Can I integrate SYNC with my existing systems?',
    answer: 'Yes! SYNC offers robust APIs and pre-built integrations with popular logistics platforms, ERPs, and accounting software. Our enterprise plan includes custom integration development.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We implement strict role-based access controls, data encryption at rest and in transit, and comprehensive audit logging. All data is backed up regularly and hosted on secure cloud infrastructure.'
  },
  {
    question: 'Do you offer a free trial?',
    answer: 'Yes, we offer a 14-day free trial with full access to all features. No credit card required. Our team will help you get started and answer any questions.'
  },
  {
    question: 'What kind of support do you provide?',
    answer: 'We offer email support for Starter plans, priority support with faster response times for Professional plans, and dedicated 24/7 support with a dedicated account manager for Enterprise customers.'
  },
  {
    question: 'Can I use SYNC on mobile devices?',
    answer: 'Yes! SYNC includes native mobile apps for both iOS and Android. Couriers can use the app for deliveries, while managers can monitor operations on the go.'
  }
]

const platformFeatures = [
  { icon: Package, title: 'Delivery Management', desc: 'Track every package from pickup to delivery' },
  { icon: Route, title: 'Smart Routing', desc: 'AI-optimized routes for maximum efficiency' },
  { icon: FileText, title: 'Document Hub', desc: 'Centralized document management' },
  { icon: Settings, title: 'Custom Workflows', desc: 'Automate your business processes' },
  { icon: Bell, title: 'Real-time Alerts', desc: 'Stay informed with instant notifications' },
  { icon: Lock, title: 'Access Control', desc: 'Fine-grained permission management' },
  { icon: TrendingUp, title: 'Growth Analytics', desc: 'Track KPIs and business metrics' },
  { icon: Calendar, title: 'Scheduling', desc: 'Advanced shift and route scheduling' },
  { icon: CreditCard, title: 'Payments', desc: 'Integrated COD and payment tracking' },
  { icon: UserCheck, title: 'Verification', desc: 'Driver and customer verification' },
  { icon: Activity, title: 'Live Monitoring', desc: 'Real-time fleet monitoring' },
  { icon: Database, title: 'Data Export', desc: 'Export data in multiple formats' }
]

// Security features (actual implemented features)
const securityFeatures = [
  { name: 'Role-Based Access', icon: Shield },
  { name: 'Data Encryption', icon: Lock },
  { name: 'Audit Logging', icon: FileText }
]

export default function Landing() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [openFaq, setOpenFaq] = useState<number | null>(null)
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null)

  const heroAnimation = useScrollAnimation()
  const featuresAnimation = useScrollAnimation()
  const statsAnimation = useScrollAnimation()
  const demoAnimation = useScrollAnimation()

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <img
                src="/images/logo.png"
                alt="SYNC Fleet"
                className="h-12 w-auto"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                  if (fallback) fallback.style.display = 'flex';
                }}
              />
              <div className="hidden items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  SYNC Fleet
                </span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
              <a href="#demo" className="text-gray-600 hover:text-blue-600 transition-colors">Demo</a>
              <a href="#pricing" className="text-gray-600 hover:text-blue-600 transition-colors">Pricing</a>
              <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-colors">Testimonials</a>
              <a href="#faq" className="text-gray-600 hover:text-blue-600 transition-colors">FAQ</a>
              <a href="#contact" className="text-gray-600 hover:text-blue-600 transition-colors">Contact</a>
            </div>

            {/* CTA Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/login"
                className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-2.5 rounded-lg font-medium hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100 py-4 animate-fadeIn">
            <div className="px-4 space-y-4">
              <a href="#features" className="block text-gray-600 hover:text-blue-600" onClick={() => setMobileMenuOpen(false)}>Features</a>
              <a href="#demo" className="block text-gray-600 hover:text-blue-600" onClick={() => setMobileMenuOpen(false)}>Demo</a>
              <a href="#pricing" className="block text-gray-600 hover:text-blue-600" onClick={() => setMobileMenuOpen(false)}>Pricing</a>
              <a href="#testimonials" className="block text-gray-600 hover:text-blue-600" onClick={() => setMobileMenuOpen(false)}>Testimonials</a>
              <a href="#faq" className="block text-gray-600 hover:text-blue-600" onClick={() => setMobileMenuOpen(false)}>FAQ</a>
              <a href="#contact" className="block text-gray-600 hover:text-blue-600" onClick={() => setMobileMenuOpen(false)}>Contact</a>
              <div className="pt-4 border-t border-gray-100 space-y-3">
                <Link to="/login" className="block text-center text-gray-600">Sign In</Link>
                <Link to="/login" className="block text-center bg-blue-600 text-white py-2 rounded-lg">Start Free Trial</Link>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-white overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div
            ref={heroAnimation.ref}
            className={`grid lg:grid-cols-2 gap-12 items-center transition-all duration-1000 ${
              heroAnimation.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
            }`}
          >
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center px-4 py-2 bg-blue-50 rounded-full text-blue-700 text-sm font-medium mb-6 animate-pulse">
                <Award className="w-4 h-4 mr-2" />
                #1 Fleet Management Platform in MENA
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
                Transform Your
                <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Fleet Operations
                </span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto lg:mx-0">
                The all-in-one ERP solution for 3PL providers and fleet owners. Manage vehicles, couriers, deliveries, HR, and finances from a single powerful platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-xl shadow-blue-500/30 hover:shadow-blue-500/50 hover:-translate-y-1"
                >
                  Start Free 14-Day Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
                <a
                  href="#demo"
                  className="inline-flex items-center justify-center px-8 py-4 bg-white text-gray-700 rounded-xl font-semibold border-2 border-gray-200 hover:border-blue-500 hover:text-blue-600 transition-all"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Watch Demo
                </a>
              </div>
              <div className="mt-8 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-sm text-gray-500">
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                  No credit card required
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                  Free onboarding
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                  Cancel anytime
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="relative z-10">
                <img
                  src="https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800&h=600&fit=crop&q=80"
                  alt="Fleet Management Dashboard"
                  className="rounded-2xl shadow-2xl hover:scale-[1.02] transition-transform duration-500"
                />
                {/* Floating Cards */}
                <div className="absolute -bottom-6 -left-6 bg-white p-4 rounded-xl shadow-xl border border-gray-100 animate-float">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <Truck className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">2,847</p>
                      <p className="text-sm text-gray-500">Active Deliveries</p>
                    </div>
                  </div>
                </div>
                <div className="absolute -top-6 -right-6 bg-white p-4 rounded-xl shadow-xl border border-gray-100 animate-float-delayed">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">1,250</p>
                      <p className="text-sm text-gray-500">Couriers Online</p>
                    </div>
                  </div>
                </div>
                {/* Additional floating element */}
                <div className="absolute top-1/2 -right-12 bg-white p-3 rounded-lg shadow-xl border border-gray-100 hidden lg:block animate-float">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-gray-700">Live Tracking</span>
                  </div>
                </div>
              </div>
              {/* Background decoration */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 blur-3xl -z-10 scale-150"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Integrations Section */}
      <section className="py-12 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm font-medium mb-6">INTEGRATED PLATFORM</p>
          <div className="flex flex-wrap justify-center items-center gap-8">
            {integrations.map((integration, index) => (
              <div
                key={index}
                className="flex items-center space-x-3 px-6 py-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <span className="text-2xl">{integration.logo}</span>
                <div>
                  <span className="font-semibold text-gray-700">{integration.name}</span>
                  <p className="text-xs text-gray-500">{integration.description}</p>
                </div>
              </div>
            ))}
            <div className="text-center text-gray-500">
              <span className="text-sm">More integrations coming soon</span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section
        ref={statsAnimation.ref}
        className={`py-16 bg-gradient-to-r from-blue-600 to-blue-800 transition-all duration-1000 ${
          statsAnimation.isVisible ? 'opacity-100' : 'opacity-0'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <p className="text-4xl sm:text-5xl font-bold text-white mb-2">
                  {statsAnimation.isVisible ? stat.value : '0'}
                </p>
                <p className="text-blue-200">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div
            ref={featuresAnimation.ref}
            className={`text-center mb-16 transition-all duration-700 ${
              featuresAnimation.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
            }`}
          >
            <span className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
              Powerful Features
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Run Your Fleet
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              A comprehensive suite of tools designed specifically for logistics companies, 3PL providers, and fleet owners in the MENA region.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`bg-white p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 cursor-pointer transform ${
                  hoveredFeature === index ? 'scale-105' : ''
                }`}
                onMouseEnter={() => setHoveredFeature(index)}
                onMouseLeave={() => setHoveredFeature(null)}
              >
                <div className={`w-14 h-14 ${feature.color} rounded-xl flex items-center justify-center mb-6 transition-transform ${
                  hoveredFeature === index ? 'scale-110 rotate-3' : ''
                }`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed mb-4">{feature.description}</p>
                <ul className={`space-y-2 overflow-hidden transition-all duration-300 ${
                  hoveredFeature === index ? 'max-h-40 opacity-100' : 'max-h-0 opacity-0'
                }`}>
                  {feature.details.map((detail, i) => (
                    <li key={i} className="flex items-center text-sm text-gray-500">
                      <CircleDot className="w-3 h-3 mr-2 text-blue-500" />
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Features Grid */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Complete Platform Capabilities
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need, all in one place
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {platformFeatures.map((feature, index) => (
              <div
                key={index}
                className="p-6 rounded-xl border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all group"
              >
                <feature.icon className="w-8 h-8 text-blue-600 mb-3 group-hover:scale-110 transition-transform" />
                <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                <p className="text-sm text-gray-500">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Live Demo Section */}
      <section id="demo" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div
            ref={demoAnimation.ref}
            className={`grid lg:grid-cols-2 gap-12 items-center transition-all duration-1000 ${
              demoAnimation.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
            }`}
          >
            <div>
              <span className="inline-block px-4 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-4">
                See It In Action
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Experience the Power of SYNC
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Watch how leading logistics companies use SYNC to streamline their operations, reduce costs, and scale their business efficiently.
              </p>
              <ul className="space-y-4 mb-8">
                {[
                  'Real-time fleet tracking with GPS integration',
                  'Automated dispatch and route optimization',
                  'Instant COD reconciliation and reporting',
                  'Mobile apps for drivers and managers'
                ].map((item, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="flex flex-wrap gap-4">
                <Link
                  to="/login"
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Try Free Demo
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
                <button className="inline-flex items-center px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold border border-gray-300 hover:border-gray-400 transition-colors">
                  <Play className="w-4 h-4 mr-2" />
                  Watch Video
                </button>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-video bg-gray-900 rounded-2xl shadow-2xl overflow-hidden relative group">
                <img
                  src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=450&fit=crop&q=80"
                  alt="Dashboard Preview"
                  className="w-full h-full object-cover opacity-80"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <button className="w-20 h-20 bg-white/90 rounded-full flex items-center justify-center shadow-xl group-hover:scale-110 transition-transform">
                    <Play className="w-8 h-8 text-blue-600 ml-1" />
                  </button>
                </div>
                <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-white/80 text-sm">
                  <span>Product Demo</span>
                  <span>3:45</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium mb-4">
              Simple Setup
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Get Started in Minutes
            </h2>
            <p className="text-xl text-gray-600">
              Simple onboarding process to get your fleet up and running
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Sign Up', desc: 'Create your account and tell us about your fleet size and requirements.', icon: UserCheck },
              { step: '02', title: 'Import Data', desc: 'Upload your vehicle and courier data or integrate with existing systems.', icon: Database },
              { step: '03', title: 'Go Live', desc: 'Start managing operations with real-time tracking and analytics.', icon: Activity }
            ].map((item, index) => (
              <div key={index} className="text-center relative group">
                <div className="text-8xl font-bold text-gray-100 absolute top-0 left-1/2 -translate-x-1/2 -z-10 group-hover:text-blue-100 transition-colors">
                  {item.step}
                </div>
                <div className="pt-12">
                  <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-600 group-hover:text-white transition-all">
                    <item.icon className="w-8 h-8 text-blue-600 group-hover:text-white transition-colors" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">{item.title}</h3>
                  <p className="text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium mb-4">
              Customer Stories
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Trusted by Industry Leaders
            </h2>
            <p className="text-xl text-gray-600">
              See what our customers have to say about SYNC
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow"
              >
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-6 italic leading-relaxed">"{testimonial.quote}"</p>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {testimonial.author.charAt(0)}
                  </div>
                  <div className="ml-4">
                    <p className="font-semibold text-gray-900">{testimonial.author}</p>
                    <p className="text-sm text-gray-500">{testimonial.role}, {testimonial.company}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
              Pricing Plans
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that fits your fleet size. All plans include a 14-day free trial.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <div
                key={index}
                className={`relative bg-white p-8 rounded-2xl border-2 transition-all hover:shadow-xl ${
                  plan.popular
                    ? 'border-blue-500 shadow-xl scale-105'
                    : 'border-gray-200 shadow-sm hover:border-blue-300'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                )}
                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-500 text-sm mb-4">{plan.description}</p>
                  <div className="flex items-baseline justify-center">
                    <span className="text-lg text-gray-500">SAR</span>
                    <span className="text-5xl font-bold text-gray-900 mx-1">{plan.price}</span>
                    <span className="text-gray-500">{plan.period}</span>
                  </div>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/login"
                  className={`block w-full py-3 rounded-lg font-semibold text-center transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 shadow-lg shadow-blue-500/25'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-4">
              FAQ
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about SYNC
            </p>
          </div>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden"
              >
                <button
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                >
                  <span className="font-semibold text-gray-900">{faq.question}</span>
                  {openFaq === index ? (
                    <ChevronUp className="w-5 h-5 text-gray-500 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-500 flex-shrink-0" />
                  )}
                </button>
                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    openFaq === index ? 'max-h-48' : 'max-h-0'
                  }`}
                >
                  <p className="px-6 pb-4 text-gray-600">{faq.answer}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Driver Mobile App Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="inline-block px-4 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium mb-4">
                Driver App
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Empower Your Drivers
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Our dedicated driver mobile app enables couriers to manage deliveries, track routes, and update status in real-time. Built with React Native for both iOS and Android platforms.
              </p>
              <ul className="space-y-3 mb-8">
                {[
                  'Real-time delivery assignments and updates',
                  'GPS navigation and route optimization',
                  'Proof of delivery with photo capture',
                  'COD collection and reconciliation',
                  'Offline mode for areas with poor connectivity'
                ].map((item, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="flex flex-wrap gap-4">
                <div className="inline-flex items-center px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold">
                  <Smartphone className="w-6 h-6 mr-3" />
                  <span>Available for iOS & Android</span>
                </div>
              </div>
            </div>
            <div className="relative flex justify-center">
              <div className="relative">
                <div className="w-64 h-[500px] bg-gray-900 rounded-[3rem] p-2 shadow-2xl">
                  <div className="w-full h-full bg-gradient-to-b from-blue-600 to-purple-600 rounded-[2.5rem] overflow-hidden">
                    <div className="h-6 flex justify-center pt-2">
                      <div className="w-20 h-5 bg-black rounded-full"></div>
                    </div>
                    <div className="p-4 space-y-4">
                      <div className="bg-white/20 backdrop-blur rounded-xl p-4">
                        <div className="text-white text-sm font-medium mb-2">Today's Deliveries</div>
                        <div className="text-white text-3xl font-bold">48</div>
                      </div>
                      <div className="bg-white/20 backdrop-blur rounded-xl p-4">
                        <div className="text-white text-sm font-medium mb-2">Active Route</div>
                        <div className="text-white text-lg font-bold">5 stops remaining</div>
                      </div>
                      <div className="bg-white/20 backdrop-blur rounded-xl p-4">
                        <div className="text-white text-sm font-medium mb-2">Status</div>
                        <div className="text-white text-lg font-bold flex items-center">
                          <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                          Online
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Decorative elements */}
                <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-yellow-400 rounded-2xl -z-10"></div>
                <div className="absolute -top-4 -left-4 w-16 h-16 bg-blue-400 rounded-xl -z-10"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Security Features Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50 border-y border-gray-200">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Enterprise-Grade Security</h3>
            <p className="text-gray-600">Your data is protected with robust security measures</p>
          </div>
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-8">
            {securityFeatures.map((feature, index) => (
              <div key={index} className="flex items-center space-x-3 px-6 py-3 bg-white rounded-lg border border-gray-200 shadow-sm">
                <feature.icon className="w-6 h-6 text-blue-600" />
                <span className="font-semibold text-gray-700">{feature.name}</span>
              </div>
            ))}
            <div className="flex items-center space-x-3 px-6 py-3 bg-white rounded-lg border border-gray-200 shadow-sm">
              <Cloud className="w-6 h-6 text-blue-600" />
              <span className="font-semibold text-gray-700">Cloud Hosted</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Fleet Operations?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join hundreds of logistics companies already using SYNC to streamline their operations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/login"
              className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 rounded-xl font-semibold hover:bg-gray-100 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-1"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
            <a
              href="#contact"
              className="inline-flex items-center justify-center px-8 py-4 bg-transparent text-white rounded-xl font-semibold border-2 border-white/50 hover:bg-white/10 transition-all"
            >
              <Headphones className="w-5 h-5 mr-2" />
              Talk to Sales
            </a>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16">
            <div>
              <span className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
                Contact Us
              </span>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Get in Touch</h2>
              <p className="text-gray-600 mb-8">
                Have questions about SYNC? Our team is here to help you find the perfect solution for your fleet management needs.
              </p>
              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="font-semibold text-gray-900">Headquarters</p>
                    <p className="text-gray-600">Riyadh, Kingdom of Saudi Arabia</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Mail className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="font-semibold text-gray-900">Email</p>
                    <p className="text-gray-600">sales@sync-fleet.com</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Phone className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="font-semibold text-gray-900">Phone</p>
                    <p className="text-gray-600">+966 11 xxx xxxx</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Clock className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="font-semibold text-gray-900">Support Hours</p>
                    <p className="text-gray-600">24/7 for Enterprise customers</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MessageCircle className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="font-semibold text-gray-900">Live Chat</p>
                    <p className="text-gray-600">Available during business hours</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
              <form className="space-y-6">
                <div className="grid sm:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      placeholder="Ahmed"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      placeholder="Al-Rashid"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Work Email</label>
                  <input
                    type="email"
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="ahmed@company.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Company</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Your Company"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Fleet Size</label>
                  <select className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all">
                    <option>Select fleet size</option>
                    <option>1-50 vehicles</option>
                    <option>51-250 vehicles</option>
                    <option>251-1000 vehicles</option>
                    <option>1000+ vehicles</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                  <textarea
                    rows={4}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                    placeholder="Tell us about your requirements..."
                  ></textarea>
                </div>
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
                >
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-5 gap-12 mb-12">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-2 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-white">SYNC</span>
              </div>
              <p className="text-gray-400 mb-6 max-w-sm">
                The leading fleet management platform for logistics companies in the MENA region. Streamline your operations, reduce costs, and scale your business.
              </p>
              <div className="flex space-x-4">
                {['twitter', 'linkedin', 'facebook', 'instagram'].map((social) => (
                  <a
                    key={social}
                    href="#"
                    className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-600 transition-colors"
                  >
                    <Globe className="w-5 h-5" />
                  </a>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-3">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Integrations</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Mobile Apps</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-3">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Press</a></li>
                <li><a href="#contact" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Support</h4>
              <ul className="space-y-3">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#faq" className="hover:text-white transition-colors">FAQ</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Community</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p>&copy; 2025 SYNC Fleet Management. All rights reserved.</p>
            <div className="flex flex-wrap justify-center gap-6 mt-4 md:mt-0">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-white transition-colors">Cookie Policy</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Custom CSS for animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes float-delayed {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
        .animate-float-delayed {
          animation: float-delayed 3s ease-in-out infinite;
          animation-delay: 1s;
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}
