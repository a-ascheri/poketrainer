// components/Pokemon/PokemonSearchModal/index.tsx
import { useEffect, useState } from 'react';
import PokemonCard from '../PokemonCard';
import PokemonDetails from '../PokemonDetails';
import { type PokemonData } from '../../../services/pokemon/pokemonService';
import './styles.scss';

interface PokemonSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function PokemonSearchModal({ isOpen, onClose }: PokemonSearchModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [pokemonData, setPokemonData] = useState<PokemonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isClosing, setIsClosing] = useState(false);

  // Cerrar con ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleClose = () => {
    setIsClosing(true); 
    setTimeout(() => {
      setIsClosing(false);
      setSearchTerm('');
      setPokemonData(null);
      setError(null);
      onClose();
    }, 250);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError(null);
    setPokemonData(null);

    try {
      const response = await fetch(`/api/v1/pokemon/${searchTerm.toLowerCase()}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Pokémon "${searchTerm}" no encontrado`);
        }
        if (response.status === 422) {
          throw new Error('Nombre de Pokémon inválido (usa solo letras, números, guiones o apóstrofes)');
        }
        throw new Error('Error al buscar el Pokémon');
      }
      
      const data = await response.json();
      setPokemonData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen && !isClosing) return null;

  if (!isOpen && !isClosing) return null;

  return (
    <>
      <div 
        className={`modal-overlay ${isClosing ? 'modal-overlay--closing' : ''}`} 
        onClick={handleClose} 
      />
      <div className={`pokemon-search-modal ${isClosing ? 'pokemon-search-modal--closing' : ''}`}>
        <button className="pokemon-search-modal__close" onClick={handleClose}>
          ✕
        </button>
        <div className="pokemon-search-modal__header">
          <h2 className="pokemon-search-modal__title">Pokédex</h2>
          <p className="pokemon-search-modal__subtitle">Ingresa nombre o ID</p>
        </div>

        <form onSubmit={handleSearch} className="pokemon-search-modal__form">
          <input
            type="text"
            placeholder="Ej: Pikachu, 25, Charizard..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => e.stopPropagation()}
            autoFocus
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </form>

        {error && (
          <div className="pokemon-search-modal__error">
            ❌ {error}
          </div>
        )}

        {pokemonData && (
          <div className="pokemon-search-modal__result">
            <PokemonCard pokemon={pokemonData} />
            <PokemonDetails pokemon={pokemonData} />
          </div>
        )}
      </div>
    </>
  );
}