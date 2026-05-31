import { FormEvent, useState } from 'react';
import PokemonCard from '../PokemonCard';
import PokemonDetails from '../PokemonDetails';
import { searchPokemon, type PokemonData } from '../../../services/pokemon/pokemonService';
import './styles.scss';

const PokemonSearch = () => {
  const [query, setQuery] = useState<string>('pikachu');
  const [pokemon, setPokemon] = useState<PokemonData | null>(null);
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsOpen(true);
    setError('');
    setIsLoading(true);

    try {
      const found = await searchPokemon(query);
      setPokemon(found);
    } catch {
      setPokemon(null);
      setError('No encontramos ese Pokémon. Probá con nombre o ID.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="search-panel">
      <button
        className="search-panel__toggle"
        type="button"
        onClick={() => setIsOpen((o) => !o)}
      >
        <span>Pokédex</span>
        <span className={`search-panel__chevron${isOpen ? ' search-panel__chevron--open' : ''}`}>▼</span>
      </button>

      {isOpen && (
        <div className="search-panel__body">
          <p className="search-panel__subtitle">Introduce nombre o ID para ver stats</p>

          <form className="search-panel__form" onSubmit={handleSubmit}>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Ej: charizard o 6"
              required
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Buscando...' : 'Buscar'}
            </button>
          </form>

          {error && <p className="search-panel__error">{error}</p>}

          {pokemon && (
            <div className="search-panel__result">
              <PokemonCard pokemon={pokemon} />
              <PokemonDetails pokemon={pokemon} />
            </div>
          )}
        </div>
      )}
    </section>
  );
};

export default PokemonSearch;
