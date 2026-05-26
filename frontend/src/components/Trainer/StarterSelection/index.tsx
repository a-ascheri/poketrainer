import { useEffect, useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import {
  getStarterOptions,
  selectStarter,
  type StarterOption,
} from '../../../services/trainer/trainerPokemonService';
import './styles.scss';

const StarterSelection = () => {
  const { refreshProfile } = useAuth();
  const [options, setOptions] = useState<StarterOption[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

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

  return (
    <section className="starter-selection">
      <h2>Elegí tu Pokémon inicial</h2>
      <p>Este paso se realiza una sola vez en tu primer login.</p>

      <div className="starter-selection__grid">
        {options.map((starter) => (
          <article key={starter.id} className="starter-selection__card">
            <img
              src={`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${starter.id}.png`}
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
  );
};

export default StarterSelection;
