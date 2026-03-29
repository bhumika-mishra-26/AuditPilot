import { CheckCircle2 } from "lucide-react";
import { useMemo } from "react";
import Hyperspeed from "../ui/Hyperspeed";

export const ValueProp = () => {
  const effectOptions = useMemo(() => ({
    "onSpeedUp": () => { },
    "onSlowDown": () => { },
    "distortion": "turbulentDistortion",
    "length": 400,
    "roadWidth": 15,
    "islandWidth": 3,
    "lanesPerRoad": 4,
    "fov": 90,
    "fovSpeedUp": 150,
    "speedUp": 2,
    "carLightsFade": 0.4,
    "totalSideLightSticks": 50,
    "lightPairsPerRoadWay": 50,
    "shoulderLinesWidthPercentage": 0.05,
    "brokenLinesWidthPercentage": 0.1,
    "brokenLinesLengthPercentage": 0.5,
    "lightStickWidth": [0.12, 0.5],
    "lightStickHeight": [1.3, 1.7],
    "movingAwaySpeed": [60, 80],
    "movingCloserSpeed": [60, 80],
    "carLightsLength": [20, 60],
    "carLightsRadius": [0.05, 0.14],
    "carWidthPercentage": [0.3, 0.5],
    "carShiftX": [-0.2, 0.2],
    "carFloorSeparation": [0.05, 1],
    "colors": {
      "roadColor": 526344,
      "islandColor": 657930,
      "background": 0,
      "shoulderLines": 1250064,
      "brokenLines": 1250064,
      "leftCars": [0xff00ff, 0xd856bf, 0xff107a],
      "rightCars": [0x00ffff, 0x03b3c3, 0x00ffcc],
      "sticks": 0x00ffff
    }
  }), []);

  const points = [
    { title: "Centralized Management", desc: "One source of truth for all your audit data and documentation." },
    { title: "Faster Reporting", desc: "Reduce report generation time by up to 60% with automated templates." },
    { title: "Clear Visibility", desc: "Real-time dashboards provide instant insight into operational risks." },
    { title: "Scalable for Teams", desc: "Built to grow with your organization, from small teams to global enterprises." },
  ];

  return (
    <section className="py-24 relative overflow-hidden min-h-[700px] flex items-center bg-black">
      <div className="absolute inset-y-0 right-0 w-full lg:w-[65%] z-0">
        <Hyperspeed effectOptions={effectOptions} />
        <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-black to-transparent pointer-events-none" />
      </div>
      <div className="max-w-7xl mx-auto px-6 relative z-10 w-full">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          <div className="lg:w-1/2">
            <h2 className="text-4xl font-bold text-white mb-8 font-heading">Why AuditPilot?</h2>
            <div className="space-y-8">
              {points.map((p, i) => (
                <div key={i} className="flex gap-4">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-cyan-500/10 flex items-center justify-center mt-1 border border-cyan-500/20">
                    <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white mb-1">{p.title}</h4>
                    <p className="text-gray-400">{p.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
