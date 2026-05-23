import React, { useState } from 'react';
import { Star } from 'lucide-react';

export default function CSATWidget({ ticketId, onSubmit }) {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (rating === 0) return;
    
    // In a real app, send to backend
    // fetch(`/api/csat`, { method: 'POST', body: JSON.stringify({ ticketId, rating, feedback }) })
    
    setSubmitted(true);
    if (onSubmit) onSubmit({ rating, feedback });
  };

  if (submitted) {
    return (
      <div className="bg-[#18191c] border border-[#10b981]/30 rounded-xl p-6 text-center animate-in fade-in">
        <h3 className="text-[#10b981] font-semibold mb-2">Thank you!</h3>
        <p className="text-sm text-gray-400">Your feedback has been recorded.</p>
      </div>
    );
  }

  return (
    <div className="bg-[#18191c] border border-[#2a2b2f] rounded-xl p-6 shadow-lg max-w-sm w-full mx-auto">
      <h3 className="text-lg font-semibold text-white mb-2 text-center">How did we do?</h3>
      <p className="text-sm text-gray-400 text-center mb-6">Please rate your experience with our support.</p>
      
      <div className="flex justify-center gap-2 mb-6">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className="focus:outline-none transition-transform hover:scale-110"
            onClick={() => setRating(star)}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(rating)}
          >
            <Star
              size={32}
              className={`${
                star <= (hover || rating) ? 'fill-amber-400 text-amber-400' : 'text-gray-600'
              } transition-colors`}
            />
          </button>
        ))}
      </div>

      {rating > 0 && (
        <div className="animate-in fade-in slide-in-from-bottom-2">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Tell us more about your experience (optional)"
            className="w-full bg-[#111214] border border-[#2a2b2f] rounded-lg p-3 text-sm text-white mb-4 focus:outline-none focus:border-[#10b981] resize-none h-24"
          />
          <button
            onClick={handleSubmit}
            className="w-full bg-[#10b981] text-black font-bold py-2.5 rounded-lg hover:bg-[#0ea5e9] transition-colors"
          >
            Submit Feedback
          </button>
        </div>
      )}
    </div>
  );
}
