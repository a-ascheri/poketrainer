import { type PokemonData } from '@services/pokemon/pokemonService';
import './styles.scss';

interface PokemonDetailsProps {
  pokemon: PokemonData;
}

const titleCase = (value: string) =>
  value.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());

const PokemonDetails = ({ pokemon }: PokemonDetailsProps) => {
  return (
    <section className="pokemon-details">
      <h4>Detalle avanzado</h4>

      <div className="pokemon-details__group">
        <strong>Habilidades</strong>
        <p>{pokemon.abilities.map(titleCase).join(', ') || 'Sin datos'}</p>
      </div>

      <div className="pokemon-details__group">
        <strong>Evolución</strong>
        <p>{pokemon.evolutionChain.map(titleCase).join(' -> ') || 'Sin evolución registrada'}</p>
      </div>

      <div className="pokemon-details__group">
        <strong>Movimientos (nivel)</strong>
        <ul>
          {pokemon.moves.slice(0, 8).map((move) => (
            <li key={move.name}>
              {titleCase(move.name)} - Nv. {move.learnLevel}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default PokemonDetails;
