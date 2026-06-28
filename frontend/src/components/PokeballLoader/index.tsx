// components/PokeballLoader/PokeballLoader.tsx
import { useEffect, useState } from 'react';
import './styles.scss';

interface PokeballLoaderProps {
  isVisible: boolean;
  onAnimationEnd?: () => void;
}

const PokeballLoader = ({ isVisible, onAnimationEnd }: PokeballLoaderProps) => {
  const [shouldRender, setShouldRender] = useState(isVisible);

  useEffect(() => {
    if (isVisible) {
      setShouldRender(true);
      // Esperar a que termine la animación de la pokebola (bounce: 1.5s + un poco más)
      const timer = setTimeout(() => {
        if (onAnimationEnd) {
          onAnimationEnd();
        }
        // Dar tiempo a que se ejecute el callback antes de desmontar
        setTimeout(() => setShouldRender(false), 100);
      }, 2000); // 1.5s de bounce + 0.5s extra para efecto visual
      
      return () => clearTimeout(timer);
    } else {
      setShouldRender(false);
    }
  }, [isVisible, onAnimationEnd]);

  if (!shouldRender) return null;

  return (
    <div className="pokeball-loader">
      <div className="pokeball">
        <div className="pokeball__top"></div>
        <div className="pokeball__bottom"></div>
        <div className="pokeball__center">
          <div className="pokeball__button"></div>
        </div>
      </div>
      <p className="pokeball-loader__text">¡Elegí tu compañero!</p>
    </div>
  );
};

export default PokeballLoader;