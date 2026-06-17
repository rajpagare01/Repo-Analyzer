import './ScoreGauge.css';

/**
 * Animated circular SVG gauge for displaying a score.
 * @param {{ score: number, label: string, size?: number }} props
 */
export default function ScoreGauge({ score, label, size = 120 }) {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (s) => {
    if (s >= 80) return 'var(--score-high)';
    if (s >= 50) return 'var(--score-medium)';
    return 'var(--score-low)';
  };

  const color = getColor(score);

  return (
    <div className="score-gauge" style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100" className="score-gauge-svg">
        {/* Background circle */}
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="8"
        />
        {/* Progress circle */}
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="score-gauge-progress"
          style={{
            '--gauge-offset': offset,
            filter: `drop-shadow(0 0 6px ${color})`,
          }}
          transform="rotate(-90 50 50)"
        />
      </svg>
      <div className="score-gauge-text">
        <span className="score-gauge-value" style={{ color }}>{score}</span>
        <span className="score-gauge-label">{label}</span>
      </div>
    </div>
  );
}
