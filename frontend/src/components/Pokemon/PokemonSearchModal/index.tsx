// frontend/src/components/Pokemon/PokemonSearchModal/index.tsx

import { useEffect, useState } from 'react';
import PokemonCard from '../PokemonCard';
import PokemonDetails from '../PokemonDetails';
import { type PokemonData } from '../../../services/pokemon/pokemonService';
import './styles.scss';

interface PokemonSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// 🔧 Validación client-side SOLO para UX (no bloqueante, solo para mostrar ayuda)
const getClientSideHint = (query: string): string | null => {
  const trimmed = query.trim();
  if (!trimmed) return null;
  
  const isNumber = /^\d+$/.test(trimmed);
  if (isNumber) {
    const id = parseInt(trimmed, 10);
    if (id > 1025) {
      return `⚠️ El ID ${id} es mayor a 1025. Es probable que no exista en la Pokédex.`;
    }
  }
  return null;
};

export default function PokemonSearchModal({ isOpen, onClose }: PokemonSearchModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [pokemonData, setPokemonData] = useState<PokemonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isClosing, setIsClosing] = useState(false);
  const [hint, setHint] = useState<string | null>(null);

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
      setHint(null);
      onClose();
    }, 250);
  };

  // Mostrar hint mientras escribe (solo UX, no bloquea)
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    setError(null);
    setHint(getClientSideHint(value));
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const trimmed = searchTerm.trim();
    if (!trimmed) {
      setError('Ingresa un nombre o ID de Pokémon');
      return;
    }
    
    // Limpiar errores anteriores
    setError(null);
    setHint(null);
    setLoading(true);
    setPokemonData(null);

    try {
      // 🔧 Enviamos la request SIN filtrar - el backend decide
      const encodedQuery = encodeURIComponent(trimmed.toLowerCase());
      const response = await fetch(`/api/v1/pokemon/${encodedQuery}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Pokémon "${searchTerm}" no encontrado`);
        }
        if (response.status === 422) {
          // 🔧 Obtener mensaje del backend
          let errorMessage = 'Nombre de Pokémon inválido';
          try {
            const errorData = await response.json();
            // El backend devuelve: {"message": "...", "errors": [...]}
            if (errorData.detail?.message) {
              errorMessage = errorData.detail.message;
            } else if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (errorData.message) {
              errorMessage = errorData.message;
            }
          } catch {
            errorMessage = 'ID o nombre de Pokémon inválido';
          }
          throw new Error(errorMessage);
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
          <p className="pokemon-search-modal__subtitle">Ingresa nombre o ID (1-1025)</p>
        </div>

        <form onSubmit={handleSearch} className="pokemon-search-modal__form">
          <input
            type="text"
            placeholder="Ej: Pikachu, 25, Charizard..."
            value={searchTerm}
            onChange={handleInputChange}
            onKeyDown={(e) => e.stopPropagation()}
            autoFocus
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </form>

        {/* Hint no bloqueante (solo sugerencia) */}
        {hint && !error && (
          <div className="pokemon-search-modal__hint">
            {hint}
          </div>
        )}

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