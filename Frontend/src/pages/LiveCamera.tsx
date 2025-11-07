import { useState, useRef, useEffect } from "react";
import { Navigation } from "@/components/ui/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Camera,
  CameraOff,
  Shield,
  Users,
  Target,
  MapPin,
  Clock,
  AlertTriangle,
  Activity,
  Zap,
  Volume2,
  VolumeX
} from "lucide-react";

const LiveCamera = () => {
  const [isActive, setIsActive] = useState(false);
  const [peopleCount, setPeopleCount] = useState(0);
  const [weaponStatus, setWeaponStatus] = useState("Safe");
  const [criminalStatus, setCriminalStatus] = useState("Safe");
  const [threatLevel, setThreatLevel] = useState<'safe' | 'warning' | 'danger'>('safe');
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [isSystemBooted, setIsSystemBooted] = useState(false);

  // 🔔 Alarm management
  const alarmRef = useRef<HTMLAudioElement | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(0.7);

  // Live video ref
  const combinedVideoRef = useRef<HTMLImageElement>(null);

  // ---------------------- START CAMERA ----------------------
  const startCamera = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/start_detection", {
        method: "POST",
      });
      if (!response.ok) throw new Error("Failed to start detection system.");
      setIsSystemBooted(true);
    } catch (error) {
      console.error("Error booting AI system:", error);
      alert("Failed to boot AI system. Check Flask logs for errors.");
      return;
    }

    setIsActive(true);
    if (combinedVideoRef.current) {
      combinedVideoRef.current.src = "http://127.0.0.1:5000/violence_feed";
    }
  };

  // ---------------------- STOP CAMERA ----------------------
  const stopCamera = () => {
    setIsActive(false);
    setPeopleCount(0);
    setThreatLevel("safe");
    setWeaponStatus("Safe");
    setCriminalStatus("Safe");
    if (combinedVideoRef.current) combinedVideoRef.current.src = "";
  };

  // ---------------------- FETCH STATUS ----------------------
  const fetchStatus = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/get_status");
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();

      const crowdCountValue = data.crowd_count.match(/\d+/g);
      const newPeopleCount = crowdCountValue ? parseInt(crowdCountValue[0], 10) : 0;
      setPeopleCount(newPeopleCount);
      setWeaponStatus(data.weapon_status);
      setCriminalStatus(data.violence_status);
      setIsBackendConnected(true);
      setIsSystemBooted(data.system_active);

      // Determine overall threat level
      if (
        data.weapon_status.toUpperCase().includes("UNSAFE") ||
        data.violence_status.toUpperCase().includes("ALERT") ||
        data.violence_status.toUpperCase().includes("CRIMINAL")
      ) {
        setThreatLevel("danger");
      } else if (newPeopleCount > 35) {
        setThreatLevel("warning");
      } else {
        setThreatLevel("safe");
      }
    } catch {
      setIsBackendConnected(false);
      setIsSystemBooted(false);
    }
  };

  useEffect(() => {
    const pollInterval = setInterval(fetchStatus, 1000);
    return () => clearInterval(pollInterval);
  }, []);

  // ---------------------- ALARM LOGIC ----------------------
  useEffect(() => {
    if (!alarmRef.current) return;

    const shouldPlayAlarm =
      threatLevel === "danger" ||
      weaponStatus.toUpperCase().includes("UNSAFE") ||
      criminalStatus.toUpperCase().includes("ALERT") ||
      criminalStatus.toUpperCase().includes("CRIMINAL") ||
      peopleCount > 35;

    alarmRef.current.volume = isMuted ? 0 : volume;

    if (shouldPlayAlarm && !isMuted) {
      if (alarmRef.current.paused) {
        alarmRef.current.loop = true;
        alarmRef.current.play().catch((err) => console.warn("Audio play blocked:", err));
      }
    } else {
      alarmRef.current.pause();
      alarmRef.current.currentTime = 0;
    }
  }, [threatLevel, weaponStatus, criminalStatus, peopleCount, isMuted, volume]);

  // ---------------------- STYLING HELPERS ----------------------
  const getThreatColor = () => {
    switch (threatLevel) {
      case "danger":
        return "text-red-400 border-red-400";
      case "warning":
        return "text-yellow-400 border-yellow-400";
      default:
        return "text-green-400 border-green-400";
    }
  };

  const getThreatBg = () => {
    switch (threatLevel) {
      case "danger":
        return "bg-red-500/10";
      case "warning":
        return "bg-yellow-500/10";
      default:
        return "bg-green-500/10";
    }
  };

  // ---------------------- MAIN JSX ----------------------
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
      <Navigation />

      {/* 🔔 Hidden alarm sound */}
      <audio ref={alarmRef} src="/sounds/alarm.mp3" preload="auto" />

      <main className="pt-20 pb-8">
        <div className="container mx-auto px-4">
          {/* Header */}
          <div className="text-center mb-8 animate-fade-in">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Shield className="h-12 w-12 text-primary animate-glow-pulse" />
              <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                Live Surveillance
              </h1>
            </div>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Advanced AI-powered weapon, criminal, and crowd monitoring system
            </p>
          </div>

          {/* Status Dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {/* Threat Level */}
            <Card className={`border-2 transition-all duration-300 ${getThreatColor()} ${getThreatBg()}`}>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Shield className="h-5 w-5" />
                  Threat Level
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold capitalize">{threatLevel}</div>
                <div className="text-sm text-muted-foreground">System Status</div>
              </CardContent>
            </Card>

            {/* People */}
            <Card className="border border-primary/20 bg-gradient-to-br from-card to-primary/5">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="h-5 w-5 text-blue-400" />
                  People Detected
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-400">{peopleCount}</div>
                <div className="text-sm text-muted-foreground">In current frame</div>
              </CardContent>
            </Card>

            {/* Weapon */}
            <Card className="border border-accent/20 bg-gradient-to-br from-card to-accent/5">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Target className="h-5 w-5 text-accent" />
                  Weapon Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-accent">
                  {weaponStatus.toUpperCase().includes("UNSAFE") ? "UNSAFE" : "SAFE"}
                </div>
                <div className="text-sm text-muted-foreground">{weaponStatus}</div>
              </CardContent>
            </Card>

            {/* Backend */}
            <Card className="border border-primary/20 bg-gradient-to-br from-card to-primary/5">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Activity className="h-5 w-5 text-primary" />
                  Backend Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${isBackendConnected ? "bg-green-400 animate-pulse" : "bg-red-400"}`}></div>
                  <span className="text-sm font-medium">
                    {isBackendConnected ? (isSystemBooted ? "RUNNING" : "ONLINE (Models OFF)") : "DISCONNECTED"}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">Port 5000</div>
              </CardContent>
            </Card>
          </div>

          {/* Main Camera Interface */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <Card className="border border-primary/20 bg-gradient-to-br from-card to-primary/5 overflow-hidden">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Camera className="h-5 w-5" />
                      Live Feed (AI Processed)
                    </div>
                    <div className="flex gap-2 items-center">
                      {/* Alarm Controls */}
                      <Button
                        onClick={() => setIsMuted(!isMuted)}
                        variant="secondary"
                        className="gap-1"
                        title={isMuted ? "Unmute Alarm" : "Mute Alarm"}
                      >
                        {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                      </Button>

                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={volume}
                        onChange={(e) => setVolume(parseFloat(e.target.value))}
                        className="w-20 accent-primary"
                      />

                      {isBackendConnected && !isActive ? (
                        <Button onClick={startCamera} variant="hero" className="gap-2">
                          <Camera className="h-4 w-4" />
                          {isSystemBooted ? "Start Monitoring" : "Start Monitoring (Boot AI)"}
                        </Button>
                      ) : (
                        <Button onClick={stopCamera} variant="destructive" className="gap-2" disabled={!isActive}>
                          <CameraOff className="h-4 w-4" />
                          Stop Monitoring
                        </Button>
                      )}
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="relative bg-black/50 aspect-video">
                    {isActive ? (
                      <img
                        key={isActive ? "live" : "offline"}
                        ref={combinedVideoRef}
                        className="w-full h-full object-cover"
                        alt="AI Processed Video Feed"
                        src={"http://127.0.0.1:5000/violence_feed"}
                      />
                    ) : (
                      <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                        <CameraOff className="h-16 w-16 mb-4 opacity-50" />
                        <p className="text-lg font-medium">Video Stream Offline</p>
                        <p className="text-sm">Click Start Monitoring to begin AI processing.</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Detection Panels */}
            <div className="space-y-6">
              {threatLevel !== "safe" && (
                <Alert className="border-red-400 bg-red-500/10 animate-pulse">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <AlertDescription className="text-red-400">
                    {threatLevel === "danger"
                      ? (weaponStatus.toUpperCase().includes("UNSAFE") ||
                        criminalStatus.toUpperCase().includes("ALERT") ||
                        criminalStatus.toUpperCase().includes("CRIMINAL"))
                        ? "CRITICAL THREAT DETECTED - Security team notified"
                        : "UNKNOWN DANGER"
                      : "HIGH CROWD DENSITY - Monitor situation"}
                  </AlertDescription>
                </Alert>
              )}

              {/* Status Cards */}
              <Card className="border border-primary/20 bg-gradient-to-br from-card to-primary/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-amber-400" />
                    Live Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* Crowd */}
                  <div className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg border border-primary/10">
                    <div className="flex items-center gap-3">
                      <Users className="h-4 w-4 text-blue-400" />
                      <div>
                        <div className="font-medium text-sm">Crowd Detection</div>
                        <div className="text-xs text-muted-foreground">{peopleCount > 35 ? "Alert" : "Safe"}</div>
                      </div>
                    </div>
                    <Badge variant={peopleCount > 35 ? "destructive" : "secondary"}>{peopleCount}</Badge>
                  </div>

                  {/* Weapon */}
                  <div className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg border border-primary/10">
                    <div className="flex items-center gap-3">
                      <Target className="h-4 w-4 text-red-400" />
                      <div>
                        <div className="font-medium text-sm">Weapon Detection</div>
                        <div className="text-xs text-muted-foreground">{weaponStatus}</div>
                      </div>
                    </div>
                    <Badge variant={weaponStatus.toUpperCase().includes("UNSAFE") ? "destructive" : "secondary"}>
                      {weaponStatus.toUpperCase().includes("UNSAFE") ? "Threat" : "Safe"}
                    </Badge>
                  </div>

                  {/* Criminal */}
                  <div className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg border border-primary/10">
                    <div className="flex items-center gap-3">
                      <Target className="h-4 w-4 text-red-400" />
                      <div>
                        <div className="font-medium text-sm">Criminal Detection</div>
                        <div className="text-xs text-muted-foreground">{criminalStatus}</div>
                      </div>
                    </div>
                    <Badge
                      variant={
                        criminalStatus.toUpperCase().includes("CRIMINAL") ||
                        criminalStatus.toUpperCase().includes("ALERT")
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {criminalStatus.toUpperCase().includes("CRIMINAL") ||
                      criminalStatus.toUpperCase().includes("ALERT")
                        ? "Threat"
                        : "Safe"}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Location */}
              <Card className="border border-primary/20 bg-gradient-to-br from-card to-primary/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-green-400" />
                    Location & Time
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="h-4 w-4 text-green-400" />
                    <span>Sector 7-G, Main Entrance</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-blue-400" />
                    <span>{new Date().toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Zap className="h-4 w-4 text-yellow-400" />
                    <span>System Online - 99.9% Uptime</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LiveCamera;
