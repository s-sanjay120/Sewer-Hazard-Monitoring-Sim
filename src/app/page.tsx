"use client";

import { useEffect, useMemo, useState } from "react";

type SectionKey = "overview" | "predict" | "forecast" | "history";

type PredictionResponse = {
  risk: string;
  anomaly: string;
  explanation: Record<string, number>;
};

type ForecastResponse = {
  predicted_methane: number;
  predicted_air_quality: number;
  predicted_temperature: number;
  predicted_humidity: number;
};

type HistoryItem = {
  ID: number;
  Methane: number;
  "Air Quality": number;
  Temperature: number;
  Humidity: number;
  Risk: string;
  Anomaly: string;
};

type SensorForm = {
  methane: number;
  air_quality: number;
  temperature: number;
  humidity: number;
};

const navigation: Array<{ id: SectionKey; label: string; description: string }> = [
  { id: "overview", label: "Overview", description: "System snapshot" },
  { id: "predict", label: "Predict", description: "Run hazard analysis" },
  { id: "forecast", label: "Forecast", description: "View next readings" },
  { id: "history", label: "History", description: "Review past predictions" },
];

const initialForm: SensorForm = {
  methane: 500,
  air_quality: 100,
  temperature: 25,
  humidity: 50,
};

function formatValue(value: number | string, suffix = "") {
  if (typeof value === "number") {
    return `${value.toFixed(1)}${suffix}`;
  }
  return `${value}${suffix}`;
}

function getRiskTone(risk: string) {
  const normalized = risk.toLowerCase();
  if (normalized.includes("safe")) {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-200";
  }
  if (normalized.includes("warning")) {
    return "border-amber-500/30 bg-amber-500/10 text-amber-200";
  }
  if (normalized.includes("critical")) {
    return "border-rose-500/30 bg-rose-500/10 text-rose-200";
  }
  return "border-sky-500/30 bg-sky-500/10 text-sky-200";
}

export default function Home() {
  const [activeSection, setActiveSection] = useState<SectionKey>("overview");
  const [form, setForm] = useState<SensorForm>(initialForm);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [forecastResponse, historyResponse] = await Promise.all([
        fetch("/api/forecast"),
        fetch("/api/history"),
      ]);

      if (!forecastResponse.ok || !historyResponse.ok) {
        throw new Error("The backend service is not reachable right now.");
      }

      const forecastData = await forecastResponse.json();
      const historyData = await historyResponse.json();
      setForecast(forecastData);
      setHistory(Array.isArray(historyData) ? historyData : []);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to load data.");
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const handlePredict = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || "Prediction request failed.");
      }

      setPrediction(data);
      await loadData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Prediction request failed.");
    } finally {
      setLoading(false);
    }
  };

  const overviewStats = useMemo(() => {
    const counts = history.reduce<Record<string, number>>((accumulator, item) => {
      accumulator[item.Risk] = (accumulator[item.Risk] ?? 0) + 1;
      return accumulator;
    }, {});

    return [
      { label: "Total Predictions", value: history.length.toString() },
      { label: "Safe", value: counts.Safe?.toString() ?? "0" },
      { label: "Warning", value: counts.Warning?.toString() ?? "0" },
      { label: "High Risk", value: counts["High Risk"]?.toString() ?? "0" },
    ];
  }, [history]);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_35%),linear-gradient(135deg,_#020617,_#0f172a_60%,_#111827)] px-2 py-4 text-slate-100 sm:px-3 lg:px-4">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 lg:flex-row">
        <aside className="w-full lg:w-64">
          <div className="rounded-2xl border border-slate-800/70 bg-slate-900/70 p-4 shadow-2xl shadow-slate-950/40 backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">Sewer Control</p>
            <h1 className="mt-2 text-xl font-semibold">AI Hazard Command Center</h1>
            <p className="mt-1 text-xs text-slate-400">
              Monitor sensor health, run predictions, review forecasts, and inspect historical events.
            </p>

            <nav className="mt-4 space-y-1.5">
              {navigation.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                    activeSection === item.id
                      ? "border-cyan-500/60 bg-cyan-500/10 text-cyan-200"
                      : "border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700 hover:text-slate-100"
                  }`}
                >
                  <div className="text-sm font-medium">{item.label}</div>
                  <div className="mt-1 text-xs text-slate-400">{item.description}</div>
                </button>
              ))}
            </nav>
          </div>
        </aside>

        <main className="flex-1 rounded-2xl border border-slate-800/70 bg-slate-900/70 p-4 shadow-2xl shadow-slate-950/40 backdrop-blur">
          {activeSection === "overview" && (
            <section className="space-y-4">
              <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">Live overview</p>
                <h2 className="mt-2 text-2xl font-semibold">Sewer hazard monitoring for rapid response</h2>
                <p className="mt-2 max-w-2xl text-xs text-slate-300">
                  The dashboard combines input data, risk analysis, forecasting and historical review in one place so operators can act quickly.
                </p>
              </div>

              <div className="grid gap-3 md:grid-cols-4">
                {overviewStats.map((stat) => (
                  <div key={stat.label} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                    <p className="text-xs text-slate-400">{stat.label}</p>
                    <p className="mt-1 text-xl font-semibold">{stat.value}</p>
                  </div>
                ))}
              </div>

              <div className="grid gap-3 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                  <h3 className="text-sm font-semibold">Latest prediction</h3>
                  {prediction ? (
                    <div className={`mt-3 rounded-xl border p-3 ${getRiskTone(prediction.risk)}`}>
                      <div className="flex items-center justify-between">
                        <span className="text-xs uppercase tracking-[0.25em]">Current status</span>
                        <span className="text-xs font-semibold">{prediction.anomaly}</span>
                      </div>
                      <p className="mt-2 text-xl font-semibold">{prediction.risk}</p>
                      <div className="mt-3 grid gap-1.5 text-xs sm:grid-cols-2">
                        {Object.entries(prediction.explanation).map(([name, value]) => (
                          <div key={name} className="rounded-lg border border-white/10 bg-slate-900/50 p-2">
                            <p className="text-slate-400">{name}</p>
                            <p className="mt-0.5 font-medium">{value.toFixed(2)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="mt-3 text-xs text-slate-400">
                      Run a new prediction from the Predict view to populate this panel.
                    </p>
                  )}
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                  <h3 className="text-sm font-semibold">Forecast snapshot</h3>
                  {forecast ? (
                    <div className="mt-3 space-y-2 text-xs text-slate-300">
                      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
                        <p className="text-slate-400">Predicted methane</p>
                        <p className="mt-0.5 text-lg font-semibold">{formatValue(forecast.predicted_methane, " ppm")}</p>
                      </div>
                      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
                        <p className="text-slate-400">Predicted air quality</p>
                        <p className="mt-0.5 text-lg font-semibold">{formatValue(forecast.predicted_air_quality, " ppm")}</p>
                      </div>
                      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
                        <p className="text-slate-400">Predicted temperature</p>
                        <p className="mt-0.5 text-lg font-semibold">{formatValue(forecast.predicted_temperature, " °C")}</p>
                      </div>
                      <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
                        <p className="text-slate-400">Predicted humidity</p>
                        <p className="mt-0.5 text-lg font-semibold">{formatValue(forecast.predicted_humidity, " %")}</p>
                      </div>
                    </div>
                  ) : (
                    <p className="mt-3 text-xs text-slate-400">Forecast values will appear once the API is available.</p>
                  )}
                </div>
              </div>
            </section>
          )}

          {activeSection === "predict" && (
            <section className="space-y-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">Prediction engine</p>
                <h2 className="mt-2 text-xl font-semibold">Run a new hazard assessment</h2>
                <p className="mt-1 text-xs text-slate-400">
                  Enter the latest sewer sensor measurements and classify the event instantly.
                </p>
              </div>

              <form onSubmit={handlePredict} className="grid gap-3 rounded-xl border border-slate-800 bg-slate-950/60 p-4 lg:grid-cols-2">
                {[
                  { key: "methane", label: "Methane", suffix: " ppm", step: 1 },
                  { key: "air_quality", label: "Air quality", suffix: " ppm", step: 1 },
                  { key: "temperature", label: "Temperature", suffix: " °C", step: 0.1 },
                  { key: "humidity", label: "Humidity", suffix: " %", step: 0.1 },
                ].map((field) => (
                  <label key={field.key} className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-300">
                    <span className="mb-1.5 block font-medium">{field.label}</span>
                    <input
                      type="number"
                      step={field.step}
                      value={form[field.key as keyof SensorForm]}
                      onChange={(event) =>
                        setForm((current) => ({
                          ...current,
                          [field.key]: Number(event.target.value),
                        }))
                      }
                      className="w-full rounded-lg border border-slate-700 bg-slate-950 px-2 py-1.5 text-sm text-slate-100 outline-none ring-0"
                    />
                    <span className="mt-1 block text-xs text-slate-500">{field.suffix}</span>
                  </label>
                ))}

                <div className="lg:col-span-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="rounded-lg bg-cyan-500 px-3 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {loading ? "Analyzing..." : "Predict hazard"}
                  </button>
                </div>
              </form>

              {error ? <p className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-2.5 text-xs text-rose-200">{error}</p> : null}

              {prediction ? (
                <div className={`rounded-xl border p-4 ${getRiskTone(prediction.risk)}`}>
                  <p className="text-xs uppercase tracking-[0.25em]">Prediction result</p>
                  <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-xl font-semibold">{prediction.risk}</p>
                      <p className="mt-0.5 text-xs">Anomaly status: {prediction.anomaly}</p>
                    </div>
                    <div className="rounded-lg border border-white/10 bg-slate-900/50 px-3 py-2 text-xs">
                      <p className="text-slate-400">Feature importance</p>
                      <p className="mt-0.5 font-medium">{Object.entries(prediction.explanation).map(([name, value]) => `${name}: ${value}`).join(" • ")}</p>
                    </div>
                  </div>
                </div>
              ) : null}
            </section>
          )}

          {activeSection === "forecast" && (
            <section className="space-y-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">Forecasting</p>
                <h2 className="mt-2 text-xl font-semibold">Next-step environmental outlook</h2>
                <p className="mt-1 text-xs text-slate-400">
                  Use the forecast section to review the expected sensor trend after the latest reading.
                </p>
              </div>

              {forecast ? (
                <div className="grid gap-3 md:grid-cols-2">
                  {[
                    { label: "Methane", value: forecast.predicted_methane, suffix: " ppm" },
                    { label: "Air quality", value: forecast.predicted_air_quality, suffix: " ppm" },
                    { label: "Temperature", value: forecast.predicted_temperature, suffix: " °C" },
                    { label: "Humidity", value: forecast.predicted_humidity, suffix: " %" },
                  ].map((item) => (
                    <div key={item.label} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                      <p className="text-xs text-slate-400">{item.label}</p>
                      <p className="mt-2 text-2xl font-semibold">{formatValue(item.value, item.suffix)}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs text-slate-400">
                  Forecast data is being loaded from the backend service.
                </p>
              )}
            </section>
          )}

          {activeSection === "history" && (
            <section className="space-y-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">History</p>
                <h2 className="mt-2 text-xl font-semibold">Review recent predictions</h2>
                <p className="mt-1 text-xs text-slate-400">
                  Every prediction is stored so operators can review patterns and respond consistently.
                </p>
              </div>

              {history.length > 0 ? (
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="min-w-full divide-y divide-slate-800 text-left text-xs">
                    <thead className="bg-slate-950/80 text-slate-300">
                      <tr>
                        <th className="px-3 py-2">ID</th>
                        <th className="px-3 py-2">Methane</th>
                        <th className="px-3 py-2">Air quality</th>
                        <th className="px-3 py-2">Temp</th>
                        <th className="px-3 py-2">Humidity</th>
                        <th className="px-3 py-2">Risk</th>
                        <th className="px-3 py-2">Anomaly</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900/60 text-slate-200">
                      {history.map((item) => (
                        <tr key={item.ID}>
                          <td className="px-3 py-2">{item.ID}</td>
                          <td className="px-3 py-2">{item.Methane}</td>
                          <td className="px-3 py-2">{item["Air Quality"]}</td>
                          <td className="px-3 py-2">{item.Temperature}</td>
                          <td className="px-3 py-2">{item.Humidity}</td>
                          <td className="px-3 py-2">{item.Risk}</td>
                          <td className="px-3 py-2">{item.Anomaly}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs text-slate-400">
                  No history is available yet. Submit a prediction to create the first record.
                </p>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
