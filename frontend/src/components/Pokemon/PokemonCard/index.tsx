import { type PokemonData } from '@services/pokemon/pokemonService';
import './styles.scss';

interface PokemonCardProps {
  pokemon: PokemonData;
}

const formatLabel = (value: string): string =>
  value.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());

const PokemonCard = ({ pokemon }: PokemonCardProps) => {
  const image = pokemon.officialArtwork || pokemon.imageUrl;

  return (
    <article className="pokemon-card">
      <div className="pokemon-card__head">
        <p className="pokemon-card__id">#{pokemon.id}</p>
        <h3>{formatLabel(pokemon.name)}</h3>
      </div>

      <div className="pokemon-card__body">
        <img src={image} alt={pokemon.name} loading="lazy" />

        <div className="pokemon-card__meta">
          <p>
            <strong>Tipo:</strong>{' '}
            {pokemon.types.map((item) => formatLabel(item.name)).join(', ')}
          </p>
          <p>
            <strong>Altura:</strong> {pokemon.height / 10} m
          </p>
          <p>
            <strong>Peso:</strong> {pokemon.weight / 10} kg
          </p>
        </div>
      </div>

      <div className="pokemon-card__stats">
        {pokemon.stats.map((stat) => (
          <div className="pokemon-card__stat" key={stat.name}>
            <span>{formatLabel(stat.name)}</span>
            <strong>{stat.value}</strong>
          </div>
        ))}
      </div>
    </article>
  );
};

export default PokemonCard;
