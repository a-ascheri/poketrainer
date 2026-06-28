import { useEffect, useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import {
  getStarterOptions,
  selectStarter,
  type StarterOption,
} from '../../../services/trainer/trainerPokemonService';
import PokeballLoader from '../../../components/PokeballLoader/index';
import './styles.scss';

const StarterSelection = () => {
  const { refreshProfile } = useAuth();
  const [options, setOptions] = useState<StarterOption[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPokeball, setShowPokeball] = useState(true);

  useEffect(() => {
    getStarterOptions()
      .then(setOptions)
      .catch(() => setError('No pudimos cargar los pokémon iniciales.'));
  }, []);

  const chooseStarter = async (name: string) => {
    setError('');
    setIsLoading(true);
    try {
      await selectStarter(name);
      await refreshProfile();
    } catch {
      setError('No se pudo seleccionar el pokémon inicial.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePokeballAnimationEnd = () => {
    setShowPokeball(false);
  };

  return (
    <>
      <PokeballLoader 
        isVisible={showPokeball} 
        onAnimationEnd={handlePokeballAnimationEnd} 
      />
      
      <section className="starter-selection">
        <h2>Elegí tu Pokémon inicial</h2>
        <p>Tu compañero te ¡ESPERA!.</p>

        <div className="starter-selection__grid">
          {options.map((starter) => (
            <article key={starter.id} className="starter-selection__card">
              <img
                src={starter.imageUrl}
                alt={starter.name}
              />
              <h3>{starter.name}</h3>
              <p>{starter.types.join(', ')}</p>
              <button disabled={isLoading} onClick={() => chooseStarter(starter.name)}>
                Seleccionar
              </button>
            </article>
          ))}
        </div>

        {error && <p className="starter-selection__error">{error}</p>}
      </section>
    </>
  );
};

export default StarterSelection;
