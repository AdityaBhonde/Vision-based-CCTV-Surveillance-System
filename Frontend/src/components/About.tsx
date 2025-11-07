import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Eye, Shield, Users, Target, AlertTriangle, Brain, Camera, Zap } from "lucide-react";

const About = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const founders = [
    { name: "Abhijit Barad", role: "Frontend Developer and Integration", avatar: "AB" },
    { name: "Palash Koul", role: "Frontend Developer and Integration", avatar: "PK" },
    { name: "Aditya Bhonde", role: "Backend and Operations Developer", avatar: "AB" },
    { name: "Kalpaj Borkute", role: "Machine Learning and Model Training", avatar: "KB" }
  ];

  const offerings = [
    {
      icon: <Eye className="w-8 h-8" />,
      title: "Value",
      description: "We help to protect buildings and infrastructure. We protect you from destruction."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Our Vision", 
      description: "Durable, strong and long-lasting protection that lasts and lasts. Our service is a customer-focused, efficient and trustworthy"
    },
    {
      icon: <Target className="w-8 h-8" />,
      title: "Our Mission",
      description: "Cater protective coating solution, combining high-quality products, expert technical support, customer service and innovation."
    }
  ];

  const solutions = [
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Detect Weapons",
      description: "Identify weapons like knives and guns in real-time using advanced deep-learning models."
    },
    {
      icon: <Camera className="w-6 h-6" />,
      title: "Recognize Faces", 
      description: "Identify known or suspicious individuals by comparing faces against a pre-loaded database."
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Generate Instant Alerts",
      description: "Automatically generates real-time alerts and logs events with timestamps, eliminating human supervision needs."
    }
  ];

  return (
    <section id="about" className="py-24 bg-gradient-to-b from-background to-muted/20 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-32 h-32 bg-primary/10 rounded-full blur-xl animate-float"></div>
        <div className="absolute bottom-20 right-10 w-24 h-24 bg-accent/10 rounded-full blur-xl animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/3 w-16 h-16 bg-primary/5 rounded-full blur-lg animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Main Header */}
        <div className={`text-center mb-20 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <Badge variant="outline" className="mb-6 px-6 py-2 text-sm font-medium border-primary/20 bg-primary/5">
            <Brain className="w-4 h-4 mr-2" />
            AI-Powered Intelligence
          </Badge>
          <h2 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            About Our System
          </h2>
          <p className="text-xl text-muted-foreground max-w-4xl mx-auto leading-relaxed">
            A Vision-Based AI-Powered CCTV Surveillance System, developed to address the critical gaps in traditional security measures and introduce an intelligent, automated layer of protection.
          </p>
        </div>

        {/* The Challenge Section */}
        <div className={`mb-20 transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <Card className="p-8 md:p-12 bg-gradient-to-br from-card to-muted/30 border-primary/20 hover:border-primary/40 transition-all duration-500">
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0">
                <div className="w-16 h-16 bg-destructive/20 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-8 h-8 text-destructive" />
                </div>
              </div>
              <div>
                <h3 className="text-3xl font-bold mb-4 text-foreground">The Challenge with Traditional Security</h3>
                <p className="text-lg text-muted-foreground leading-relaxed">
                  In today's world, ensuring public safety in sensitive areas like campuses, offices, and public spaces is a major concern. Standard CCTV systems are passive, merely recording video footage that requires constant, tiring, and often inefficient manual monitoring. This reactive approach means threats are often noticed only after an incident has occurred.
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Our Intelligent Solution Section */}
        <div className={`mb-20 transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="text-center mb-12">
            <h3 className="text-4xl font-bold mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Our Intelligent Solution
            </h3>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              Our project transforms surveillance from a passive recording tool into a proactive, real-time threat detection system. By integrating sophisticated computer vision and machine learning, our system actively analyzes video feeds to:
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {solutions.map((solution, index) => (
              <Card key={index} className={`p-6 bg-gradient-to-br from-card to-muted/20 border-primary/20 hover:border-primary/40 transition-all duration-500 hover:shadow-glow group animate-fade-in`} style={{ animationDelay: `${index * 200}ms` }}>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center group-hover:bg-primary/30 transition-colors">
                      {solution.icon}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-xl font-semibold mb-3 text-foreground">{solution.title}</h4>
                    <p className="text-muted-foreground leading-relaxed">{solution.description}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* What We Offer Section */}
        <div className={`mb-20 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="text-center mb-12">
            <h3 className="text-4xl font-bold mb-6">
              What We <span className="text-primary">Offer</span>
            </h3>
            <p className="text-muted-foreground">Don't forget to check these real success.</p>
            <div className="flex justify-center mt-4">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-primary rounded-full"></div>
                <div className="w-3 h-3 bg-primary/60 rounded-full"></div>
                <div className="w-3 h-3 bg-primary/30 rounded-full"></div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {offerings.map((offering, index) => (
              <Card key={index} className={`p-8 text-center bg-gradient-to-br from-card to-muted/20 border-primary/20 hover:border-primary/40 transition-all duration-500 hover:shadow-glow hover:scale-105 group animate-fade-in`} style={{ animationDelay: `${index * 150}ms` }}>
                <div className="flex justify-center mb-6">
                  <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center group-hover:bg-primary/30 transition-colors text-primary">
                    {offering.icon}
                  </div>
                </div>
                <h4 className="text-2xl font-bold mb-4 text-foreground">{offering.title}</h4>
                <p className="text-muted-foreground leading-relaxed">{offering.description}</p>
              </Card>
            ))}
          </div>
        </div>

        {/* Founders Section */}
        <div className={`transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="text-center mb-12">
            <h3 className="text-4xl font-bold mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Meet Our Founders
            </h3>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              The visionary team behind the revolutionary AI surveillance technology
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {founders.map((founder, index) => (
              <Card key={index} className={`p-6 text-center bg-gradient-to-br from-card to-muted/20 border-primary/20 hover:border-primary/40 transition-all duration-500 hover:shadow-glow hover:scale-105 group animate-fade-in`} style={{ animationDelay: `${index * 100}ms` }}>
                <div className="flex justify-center mb-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center text-primary-foreground font-bold text-xl group-hover:scale-110 transition-transform">
                    {founder.avatar}
                  </div>
                </div>
                <h4 className="text-xl font-bold mb-2 text-foreground">{founder.name}</h4>
                <p className="text-primary text-sm font-medium">{founder.role}</p>
              </Card>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className={`text-center mt-20 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <p className="text-xl text-muted-foreground">
            This innovative approach enhances security, reduces manual effort, and provides the early warnings needed to prevent critical incidents.
          </p>
        </div>
      </div>
    </section>
  );
};

export { About };