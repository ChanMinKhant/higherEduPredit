import React from 'react'
import { getRecentPredictions } from '../../services/predict';
import { useUser } from '../../hooks/useUser';

export default function RecentPrediction() {
  const [predictions, setPredictions] = React.useState<any[]>([]);
  const { user, loading } = useUser();

  React.useEffect(() => {
    const fetchRecentPredictions = async () => {
      if (!user) return; // ✅ wait until user is available

      try {
        const data = await getRecentPredictions(user._id);
        setPredictions(data);
      } catch (error) {
        console.error("Error fetching recent predictions:", error);
      }
    };

    fetchRecentPredictions();
  }, [user]);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Recent Predictions</h2>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : predictions.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {predictions.map((p: any) => (
            <div 
              key={p._id} 
              className="bg-white shadow-md rounded-2xl p-5 hover:shadow-lg transition"
            >
              <h3 className="text-lg font-semibold mb-2">
                {p.result.pass_fail === "pass" ? (
                  <span className="text-green-600">✅ PASS</span>
                ) : (
                  <span className="text-red-600">❌ FAIL</span>
                )}
              </h3>

              <p className="text-gray-700">
                <span className="font-medium">Predicted Grade:</span> {p.result.predicted_grade}
              </p>
              <p className="text-gray-700">
                <span className="font-medium">Confidence:</span> {p.result.confidence}
              </p>
              <p className="text-gray-700">
                <span className="font-medium">Higher Education:</span> {p.result.higher_education}
              </p>
              <p className="text-gray-700 text-sm mt-3">
                <span className="font-medium">Predicted date:</span>{" "}
                {new Date(p.createdAt).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No predictions found.</p>
      )}
    </div>
  );
}
