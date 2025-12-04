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
  VolumeX,
} from "lucide-react";

const LiveCamera = () => {
  const [isActive, setIsActive] = useState(false);
  const [peopleCount, setPeopleCount] = useState(0);

  // DETECTION STATES
  const [weaponStatus, setWeaponStatus] = useState("Safe");
  const [criminalStatus, setCriminalStatus] = useState("Safe");

  // SYSTEM STATES
  const [threatLevel, setThreatLevel] = useState<"safe" | "warning" | "danger">("safe");
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [isSystemBooted, setIsSystemBooted] = useState(false);

  // MEMORY: last high-confidence weapon detection (≥ 0.60)
  const [lastHighWeaponTime, setLastHighWeaponTime] = useState(0);

  // Alarm audio
  const alarmRef = useRef<HTMLAudioElement | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(0.7);

  // Video reference
  const combinedVideoRef = useRef<HTMLImageElement>(null);

  // ==================================================================================
  // START CAMERA
  // ==================================================================================
  const startCamera = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/start_detection", {
        method: "POST",
      });
      if (!response.ok) throw new Error();
      setIsSystemBooted(true);
    } catch {
      alert("Backend not running! Please start Flask server on port 5000.");
      return;
    }

    setIsActive(true);
    if (combinedVideoRef.current) {
      combinedVideoRef.current.src = "http://127.0.0.1:5000/violence_feed";
    }
  };

  // ==================================================================================
  // STOP CAMERA
  // ==================================================================================
  const stopCamera = () => {
    setIsActive(false);
    setPeopleCount(0);
    setWeaponStatus("Safe");
    setCriminalStatus("Safe");
    setThreatLevel("safe");
    setLastHighWeaponTime(0);

    if (combinedVideoRef.current) combinedVideoRef.current.src = "";
  };

  // ==================================================================================
  // FETCH STATUS FROM BACKEND
  // ==================================================================================
  const fetchStatus = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get_status");
      if (!res.ok) throw new Error();
      const data = await res.json();

      setIsBackendConnected(true);
      setIsSystemBooted(data.system_active ?? false);

      // -------- CROWD COUNT --------
      const matchCrowd = (data.crowd_count ?? "").match(/\d+/);
      const crowd = matchCrowd ? parseInt(matchCrowd[0], 10) : 0;
      setPeopleCount(crowd);

      // =====================================================
      // WEAPON DETECTION WITH CONFIDENCE FILTER (≥ 0.60)
      // =====================================================
      let rawWeaponString = data.weapon_status ? data.weapon_status : "Safe";
      let extractedConf = 0;

      // Extract confidence from string like "Knife detected (0.62)"
      const wm = rawWeaponString.match(/\((.*?)\)/);
      if (wm) extractedConf = parseFloat(wm[1]);

      // Only show weapon threat if confidence >= 0.60
      if (extractedConf >= 0.60) {
        setWeaponStatus(rawWeaponString);
        setLastHighWeaponTime(Date.now()); // Remember when we saw high-confidence weapon
      } else {
        setWeaponStatus("Safe");
      }

      // -------- CRIMINAL DETECTION --------
      setCriminalStatus(data.violence_status ?? "Safe");

      // =====================================================
      // THREAT LEVEL CALCULATION
      // =====================================================
      // Check if we recently saw a high-confidence weapon (within last 1.5 seconds)
      const weaponThreat = Date.now() - lastHighWeaponTime < 1500;

      // Check if criminal activity detected
      const criminalThreat =
        (data.violence_status ?? "").toUpperCase().includes("CRIMINAL") ||
        (data.violence_status ?? "").toUpperCase().includes("ALERT");

      // Set threat level based on all conditions
      if (weaponThreat || criminalThreat) {
        setThreatLevel("danger");
      } else if (crowd > 35) {
        setThreatLevel("warning");
      } else {
        setThreatLevel("safe");
      }
    } catch {
      setIsBackendConnected(false);
      setIsSystemBooted(false);
    }
  };

  // Poll backend every 1 second
  useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, 1000);
    return () => clearInterval(timer);
  }, [lastHighWeaponTime]); // Re-run when weapon time changes

  // ==================================================================================
  // ALARM SYSTEM - Rings when ANY threat is detected
  // ==================================================================================
  useEffect(() => {
    if (!alarmRef.current) return;

    // Check if we recently detected weapon (within 1.5 seconds)
    const weaponThreat = Date.now() - lastHighWeaponTime < 1500;

    // Check if criminal detected
    const criminalThreat =
      criminalStatus.toUpperCase().includes("CRIMINAL") ||
      criminalStatus.toUpperCase().includes("ALERT");

    // Check if crowd is too high
    const crowdThreat = peopleCount > 35;

    // Play alarm if ANY threat exists
    const shouldPlay = weaponThreat || criminalThreat || crowdThreat;

    alarmRef.current.volume = isMuted ? 0 : volume;

    if (shouldPlay && !isMuted) {
      alarmRef.current.loop = true;
      if (alarmRef.current.paused) {
        alarmRef.current.play().catch(() => {});
      }
    } else {
      alarmRef.current.pause();
      alarmRef.current.currentTime = 0;
    }
  }, [criminalStatus, lastHighWeaponTime, peopleCount, isMuted, volume]);

  // ==================================================================================
  // UI HELPERS
  // ==================================================================================
  const getThreatColor = () =>
    threatLevel === "danger"
      ? "text-red-400 border-red-400"
      : threatLevel === "warning"
      ? "text-yellow-400 border-yellow-400"
      : "text-green-400 border-green-400";

  const getThreatBg = () =>
    threatLevel === "danger"
      ? "bg-red-500/10"
      : threatLevel === "warning"
      ? "bg-yellow-500/10"
      : "bg-green-500/10";

  // Check individual threats for alerts
  const hasWeaponThreat = Date.now() - lastHighWeaponTime < 1500;
  const hasCriminalThreat =
    criminalStatus.toUpperCase().includes("CRIMINAL") ||
    criminalStatus.toUpperCase().includes("ALERT");
  const hasCrowdThreat = peopleCount > 35;

  // ==================================================================================
  // UI RENDER
  // ==================================================================================
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
      <Navigation />

      <audio ref={alarmRef} src="/sounds/alarm.mp3" preload="auto" />

      <main className="pt-20 pb-8">
        <div className="container mx-auto px-4">

          {/* HEADER */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Shield className="h-12 w-12 text-primary" />
              <h1 className="text-6xl font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                Live Surveillance
              </h1>
            </div>
            <p className="text-lg text-muted-foreground">
              Real-time AI Monitoring: Weapons • Criminals • Crowd Density
            </p>
          </div>

          {/* STATUS CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">

            {/* THREAT CARD */}
            <Card className={`border-2 ${getThreatColor()} ${getThreatBg()}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Shield className="h-5 w-5" /> Threat Level
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold capitalize">{threatLevel}</div>
                <div className="text-sm text-muted-foreground">System Status</div>
              </CardContent>
            </Card>

            {/* CROWD CARD */}
            <Card className={`border ${hasCrowdThreat ? 'border-yellow-400/50 bg-yellow-500/10' : 'border-blue-400/20 bg-blue-500/5'}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="h-5 w-5 text-blue-400" /> Crowd Count
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold ${hasCrowdThreat ? 'text-yellow-400' : 'text-blue-400'}`}>
                  {peopleCount}
                </div>
                <div className="text-sm text-muted-foreground">
                  {hasCrowdThreat ? "⚠ High Density" : "Normal"}
                </div>
              </CardContent>
            </Card>

            {/* WEAPON CARD */}
            <Card className={`border ${hasWeaponThreat ? 'border-red-400/50 bg-red-500/10' : 'border-red-400/20 bg-red-500/5'}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Target className="h-5 w-5 text-red-400" /> Weapon Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold text-red-400 ${hasWeaponThreat ? 'animate-pulse' : ''}`}>
                  {weaponStatus !== "Safe" ? "UNSAFE" : "SAFE"}
                </div>
                <div className="text-sm text-muted-foreground">{weaponStatus}</div>
              </CardContent>
            </Card>

            {/* BACKEND STATUS */}
            <Card className="border border-primary/20 bg-primary/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Activity className="h-5 w-5 text-primary" /> Backend Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    isBackendConnected ? "bg-green-400 animate-pulse" : "bg-red-400"
                  }`}></div>
                  <span className="text-sm">
                    {isBackendConnected
                      ? (isSystemBooted ? "RUNNING" : "ONLINE")
                      : "OFFLINE"}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* CAMERA + RIGHT PANEL */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

            {/* CAMERA FEED */}
            <div className="lg:col-span-2">
              <Card className="border border-primary/20 bg-primary/5 overflow-hidden">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Camera className="h-5 w-5" /> Live Feed
                    </div>
                    <div className="flex items-center gap-2">

                      <Button onClick={() => setIsMuted(!isMuted)} variant="secondary">
                        {isMuted ? <VolumeX /> : <Volume2 />}
                      </Button>

                      <input
                        type="range"
                        min="0" max="1" step="0.1"
                        value={volume}
                        onChange={(e) => setVolume(parseFloat(e.target.value))}
                        className="w-20"
                      />

                      {isBackendConnected && !isActive ? (
                        <Button variant="hero" onClick={startCamera}>
                          <Camera className="mr-1" /> Start Monitoring
                        </Button>
                      ) : (
                        <Button variant="destructive" disabled={!isActive} onClick={stopCamera}>
                          <CameraOff className="mr-1" /> Stop
                        </Button>
                      )}
                    </div>
                  </CardTitle>
                </CardHeader>

                <CardContent className="p-0">
                  <div className="relative bg-black/50 aspect-video">
                    {isActive ? (
                      <img
                        ref={combinedVideoRef}
                        className="w-full h-full object-cover"
                        src="http://127.0.0.1:5000/violence_feed"
                        alt="Live Feed"
                      />
                    ) : (
                      <div className="flex flex-col items-center justify-center h-full">
                        <CameraOff className="h-16 w-16 opacity-50" />
                        <p className="text-lg">Video Offline</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* RIGHT PANEL */}
            <div className="space-y-4">

              {/* ============ WEAPON ALERT ============ */}
              {hasWeaponThreat && (
                <Alert className="border-red-400 bg-red-600/10 animate-pulse">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <AlertDescription className="text-red-400 font-semibold">
                    🚨 WEAPON DETECTED — SECURITY ALERT ISSUED
                  </AlertDescription>
                </Alert>
              )}

              {/* ============ CRIMINAL ALERT ============ */}
              {hasCriminalThreat && (
                <Alert className="border-red-400 bg-red-600/10 animate-pulse">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <AlertDescription className="text-red-400 font-semibold">
                    🚨 CRIMINAL ACTIVITY DETECTED — SECURITY ALERT ISSUED
                  </AlertDescription>
                </Alert>
              )}

              {/* ============ CROWD ALERT ============ */}
              {hasCrowdThreat && !hasWeaponThreat && !hasCriminalThreat && (
                <Alert className="border-yellow-400 bg-yellow-600/10 animate-pulse">
                  <AlertTriangle className="h-4 w-4 text-yellow-400" />
                  <AlertDescription className="text-yellow-400 font-semibold">
                    ⚠ HIGH CROWD DENSITY ({peopleCount} people) — Monitor situation
                  </AlertDescription>
                </Alert>
              )}

              {/* STATUS LIST */}
              <Card className="border border-primary/20 bg-primary/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-yellow-400" /> Live Status
                  </CardTitle>
                </CardHeader>

                <CardContent className="space-y-3">

                  {/* CROWD STATUS */}
                  <div className="flex justify-between p-3 bg-secondary/20 rounded-lg border">
                    <div className="flex items-center gap-3">
                      <Users className="h-4 w-4 text-blue-400" />
                      <div>
                        <div className="text-sm font-medium">Crowd Detection</div>
                        <div className="text-xs text-muted-foreground">
                          {hasCrowdThreat ? "⚠ Alert" : "✓ Safe"}
                        </div>
                      </div>
                    </div>
                    <Badge variant={hasCrowdThreat ? "destructive" : "secondary"}>
                      {peopleCount}
                    </Badge>
                  </div>

                  {/* WEAPON STATUS */}
                  <div className="flex justify-between p-3 bg-secondary/20 rounded-lg border">
                    <div className="flex items-center gap-3">
                      <Target className="h-4 w-4 text-red-400" />
                      <div>
                        <div className="text-sm font-medium">Weapon Detection</div>
                        <div className="text-xs text-muted-foreground">{weaponStatus}</div>
                      </div>
                    </div>
                    <Badge variant={weaponStatus !== "Safe" ? "destructive" : "secondary"}>
                      {weaponStatus !== "Safe" ? "🚨 Threat" : "✓ Safe"}
                    </Badge>
                  </div>

                  {/* CRIMINAL */}
                  <div className="flex justify-between p-3 bg-secondary/20 rounded-lg border">
                    <div className="flex items-center gap-3">
                      <Target className="h-4 w-4 text-red-400" />
                      <div>
                        <div className="text-sm font-medium">Criminal Detection</div>
                        <div className="text-xs text-muted-foreground">{criminalStatus}</div>
                      </div>
                    </div>
                    <Badge variant={hasCriminalThreat ? "destructive" : "secondary"}>
                      {hasCriminalThreat ? "🚨 Threat" : "✓ Safe"}
                    </Badge>
                  </div>

                </CardContent>
              </Card>

              {/* LOCATION */}
              <Card className="border border-primary/20 bg-primary/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-green-400" /> Location & Time
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="h-4 w-4 text-green-400" />
                    Sector 7-G, Main Entrance
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-blue-400" />
                    {new Date().toLocaleString()}
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Zap className="h-4 w-4 text-yellow-400" />
                    System Online — 99.9% Uptime
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
