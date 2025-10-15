import { memo } from 'react';
import Lottie from 'lottie-react';

import LottieWaitlist from '../assets/wired-outline-1140-error-hover-enlarge.json';
import LottieShortlisted from '../assets/wired-outline-37-approve-checked-simple-hover-wobble.json';
import LottieRejected from '../assets/wired-outline-1122-thumb-down-hover-down.json';

const map = {
  review: LottieWaitlist,
  shortlisted: LottieShortlisted,
  rejected: LottieRejected,
};

function StatusLottie({ type, size = 20, loop = true, speed = 0.9, className = '' }) {
  const anim = map[type] || map.review;
  return (
    <Lottie
      animationData={anim}
      loop={loop}
      autoplay
      className={className}
      style={{ width: size, height: size, pointerEvents: 'none' }}
      rendererSettings={{ preserveAspectRatio: 'xMidYMid slice', clearCanvas: true }}
      speed={speed}
      aria-hidden
    />
  );
}

export default memo(StatusLottie);
