import { Card } from "@/components/ui/card";
import { Shield, Brain, Zap, Camera, Users, AlertTriangle } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Detection",
    description: "Advanced deep learning models using YOLOv8 and Faster R-CNN for weapon and violence detection with superior accuracy.",
    gradient: "from-primary to-accent"
  },
  {
    icon: Zap,
    title: "Real-time Processing",
    description: "Lightning-fast inference on live surveillance feeds with instant threat identification and response automation.",
    gradient: "from-accent to-primary"
  },
  {
    icon: AlertTriangle,
    title: "Instant Alerts",
    description: "Immediate Telegram notifications with snapshots, confidence scores, and detailed incident information.",
    gradient: "from-destructive to-primary"
  },
  {
    icon: Camera,
    title: "Multi-Camera Support",
    description: "Scalable architecture supporting multiple CCTV cameras with centralized monitoring and management.",
    gradient: "from-primary to-accent"
  },
  {
    icon: Users,
    title: "Crowd Analysis",
    description: "Advanced crowd density estimation and anomaly detection for early warning in high-risk situations.",
    gradient: "from-accent to-primary"
  },
  {
    icon: Shield,
    title: "Security First",
    description: "Enterprise-grade security with data encryption, privacy protection, and secure authentication systems.",
    gradient: "from-primary to-destructive"
  }
];

export function Features() {
  return (
    <section className="py-20 bg-gradient-to-b from-background to-card/20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Advanced AI Capabilities
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Cutting-edge technology stack powering the next generation of intelligent surveillance systems
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className="p-6 bg-gradient-to-br from-card to-card/50 border-border/50 hover:border-primary/50 transition-all duration-300 group hover:shadow-tech animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="mb-4">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.gradient} p-2.5 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-full h-full text-white" />
                </div>
              </div>
              <h3 className="text-xl font-semibold mb-3 text-foreground group-hover:text-primary transition-colors">
                {feature.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}