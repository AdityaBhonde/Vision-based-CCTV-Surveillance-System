import { Badge } from "@/components/ui/badge";

const technologies = [
  { name: "Python", category: "Backend" },
  { name: "PyTorch", category: "AI/ML" },
  { name: "YOLOv8", category: "AI/ML" },
  { name: "Faster R-CNN", category: "AI/ML" },
  { name: "OpenCV", category: "Computer Vision" },
  { name: "React.js", category: "Frontend" },
  { name: "MongoDB", category: "Database" },
  { name: "Telegram API", category: "Alerts" },
  { name: "TensorFlow", category: "AI/ML" },
  { name: "JavaScript", category: "Frontend" }
];

export function TechStack() {
  return (
    <section className="py-20 bg-gradient-to-b from-card/20 to-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
              Powered by Modern Technology
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Built with industry-leading technologies and frameworks for maximum performance and reliability
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
          {technologies.map((tech, index) => (
            <Badge 
              key={index}
              variant="secondary" 
              className="px-4 py-2 text-sm bg-card/50 border border-border hover:border-primary/50 hover:bg-primary/10 transition-all duration-300 animate-fade-in"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <span className="text-primary font-medium">{tech.name}</span>
              <span className="text-muted-foreground ml-2 text-xs">• {tech.category}</span>
            </Badge>
          ))}
        </div>

        {/* Architecture Overview */}
        <div className="mt-16 max-w-3xl mx-auto">
          <div className="bg-gradient-to-br from-card to-card/50 rounded-xl border border-border/50 p-8">
            <h3 className="text-xl font-semibold mb-6 text-center">System Architecture</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full mx-auto mb-3 flex items-center justify-center">
                  <span className="text-white font-bold">AI</span>
                </div>
                <h4 className="font-semibold mb-2">AI Processing</h4>
                <p className="text-sm text-muted-foreground">Deep learning models for real-time detection</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-accent to-primary rounded-full mx-auto mb-3 flex items-center justify-center">
                  <span className="text-white font-bold">API</span>
                </div>
                <h4 className="font-semibold mb-2">Backend Services</h4>
                <p className="text-sm text-muted-foreground">Microservice architecture with RESTful APIs</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full mx-auto mb-3 flex items-center justify-center">
                  <span className="text-white font-bold">UI</span>
                </div>
                <h4 className="font-semibold mb-2">Frontend Dashboard</h4>
                <p className="text-sm text-muted-foreground">Responsive web interface for monitoring</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}