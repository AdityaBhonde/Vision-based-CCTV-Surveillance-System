import { Button } from "@/components/ui/button";
import { ArrowRight, Play, Shield, Zap, Eye } from "lucide-react";
import heroImage from "@/assets/hero-bg.jpg";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <img 
          src={heroImage} 
          alt="AI Surveillance Control Room" 
          className="w-full h-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background/90 via-background/70 to-background/90"></div>
      </div>

      {/* Animated Background Elements */}
      <div className="absolute inset-0 z-10">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-primary rounded-full animate-float opacity-60"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-accent rounded-full animate-float opacity-40" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-primary/30 rounded-full animate-float" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Main Content */}
      <div className="relative z-20 container mx-auto px-4 text-center">
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
          {/* Brand Badge */}
          <div className="inline-flex items-center space-x-2 bg-card/50 backdrop-blur-sm border border-border rounded-full px-4 py-2 animate-slide-in-left">
            <Shield className="h-4 w-4 text-primary" />
            <span className="text-sm text-muted-foreground">Code Republic</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold leading-tight">
            <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-glow-pulse">
              VISION BASED
            </span>
            <br />
            <span className="text-foreground">
              AI-POWERED CCTV
            </span>
            <br />
            <span className="bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
              SURVEILLANCE SYSTEM
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Cutting-edge AI-powered surveillance technology for defense and civilian security applications. 
            Real-time threat detection with 99%+ accuracy across land and aquatic environments.
          </p>

          {/* Features Pills */}
          <div className="flex flex-wrap justify-center gap-4 my-8">
            <div className="flex items-center space-x-2 bg-card/30 backdrop-blur-sm border border-border rounded-full px-4 py-2">
              <Eye className="h-4 w-4 text-primary" />
              <span className="text-sm">Real-time Detection</span>
            </div>
            <div className="flex items-center space-x-2 bg-card/30 backdrop-blur-sm border border-border rounded-full px-4 py-2">
              <Zap className="h-4 w-4 text-accent" />
              <span className="text-sm">Instant Alerts</span>
            </div>
            <div className="flex items-center space-x-2 bg-card/30 backdrop-blur-sm border border-border rounded-full px-4 py-2">
              <Shield className="h-4 w-4 text-primary" />
              <span className="text-sm">99%+ Accuracy</span>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex justify-center items-center">
            <Button variant="outline" size="lg" className="group bg-card/20 backdrop-blur-sm">
              <Play className="h-4 w-4 transition-transform group-hover:scale-110" />
              Watch Demo
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 pt-8 border-t border-border/30">
            <div className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-primary">99%+</div>
              <div className="text-sm text-muted-foreground">Accuracy Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-accent">24/7</div>
              <div className="text-sm text-muted-foreground">Monitoring</div>
            </div>
            <div className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-primary">Real-time</div>
              <div className="text-sm text-muted-foreground">Processing</div>
            </div>
            <div className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-accent">Instant</div>
              <div className="text-sm text-muted-foreground">Alerts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-primary rounded-full flex justify-center">
          <div className="w-1 h-3 bg-primary rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
}