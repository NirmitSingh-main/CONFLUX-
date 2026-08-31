/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { MissionProvider, useMission } from "./context/MissionContext";
import { Shell } from "./components/layout/Shell";
import { Dashboard } from "./pages/Dashboard";
import { Missions } from "./pages/Missions";
import { Telemetry } from "./pages/Telemetry";
import { Thermal } from "./pages/Thermal";
import { Wavefront } from "./pages/Wavefront";
import { Orbital } from "./pages/Orbital";
import { SpaceWeather } from "./pages/SpaceWeather";
import { Fusion } from "./pages/Fusion";

function MainRouter() {
  const { activePage } = useMission();

  const renderActivePage = () => {
    switch (activePage) {
      case "overview":
        return <Dashboard />;
      case "missions":
        return <Missions />;
      case "telemetry":
        return <Telemetry />;
      case "thermal":
        return <Thermal />;
      case "wavefront":
        return <Wavefront />;
      case "orbital":
        return <Orbital />;
      case "weather":
        return <SpaceWeather />;
      case "fusion":
        return <Fusion />;
      default:
        return <Dashboard />;
    }
  };

  return <Shell>{renderActivePage()}</Shell>;
}

export default function App() {
  return (
    <MissionProvider>
      <MainRouter />
    </MissionProvider>
  );
}
