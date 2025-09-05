import React from 'react';
import { getRecentPredictions } from '../../services/predict';
import { useUser } from '../../hooks/useUser';
import { Link, useParams, useNavigate } from 'react-router-dom';

export default function RecentPrediction() {
  const [predictions, setPredictions] = React.useState<any[]>([]);
  const { user, loading } = useUser();
  const { userid } = useParams<{ userid?: string }>();
  const navigate = useNavigate();

  React.useEffect(() => {
    const fetchRecentPredictions = async () => {
      if (!user) return;

      // If userid param exists, check if user is admin
      if (userid && user.role !== 'admin') {
        navigate('/'); // redirect if not admin
        return;
      }

      try {
        const idToFetch = userid || user._id;
        console.log(idToFetch)
        const data = await getRecentPredictions(idToFetch);
        console.log('recent predictions:', data);
        setPredictions(data);
      } catch (error) {
        console.error("Error fetching recent predictions:", error);
      }
    };

    fetchRecentPredictions();
  }, [user, userid, navigate]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    navigate('/');
    return null;
  }

  return (
    <div className="w-full flex flex-col items-center mt-10">
      <div className="w-full flex justify-center mb-6">
        <div className="w-[90%] m-auto flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold mb-6">Recent Predictions</h2>
          <Link to="/predict" className="text-blue-500 hover:underline">
            More predictions
          </Link>
        </div>
      </div>

      {predictions.length > 0 ? (
        <div className="flex flex-wrap gap-6 justify-start w-[90%] m-auto">
          {predictions.map((p: any) => (
            <div
              key={p._id}
              className="flex justify-center rounded-2xl shadow-sm hover:shadow-md transition h-[200px] w-[400px] border border-gray-200 bg-white"
            >
              <div className="flex flex-col justify-evenly items-stretched w-[90%] m-auto p-4 h-full">
                <h3 className="text-lg font-semibold mb-2">
                  {p.result.pass_fail === 'pass' ? (
                    <span className="text-green-600">✅ PASS</span>
                  ) : (
                    <span className="text-red-600">❌ FAIL</span>
                  )}
                </h3>

                <p className="text-gray-700">
                  <span className="font-medium">Success Chance:</span>{' '}
                  {(p.result.probability_pass * 100).toFixed(2)}%
                </p>
                <p className="text-gray-700">
                  <span className="font-medium">Confidence:</span> {p.result.confidence}
                </p>
                <p className="text-gray-700">
                  <span className="font-medium">Higher Education:</span> {p.result.higher_education}
                </p>
                <p className="text-gray-700 text-sm mt-3">
                  <span className="font-medium">Predicted date:</span>{' '}
                  {new Date(p.createdAt).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No predictions found.</p>
      )}
    </div>
  );
}
