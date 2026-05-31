import { useCallback, useEffect, useRef, useState } from 'react';
import { type GameSave, gameService } from '../../../services/game/gameService';
import PhaserGame from '../PhaserGame';
import './styles.scss';

type GameStatus = 'off' | 'loading' | 'running' | 'error';

/** Dimensiones internas del canvas de juego */
const GAME_WIDTH = 320;
const GAME_HEIGHT = 288;

const KEY_DIR: Record<string, keyof DpadReactive> = {
  ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
};

interface DpadReactive {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

export default function GameShell() {
  const [status, setStatus] = useState<GameStatus>('off');
  const [saveData, setSaveData] = useState<GameSave | null>(null);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'error'>('idle');
  /** Last known player position + map, updated every autosave tick. */
  const lastKnownPosRef = useRef({ tileX: 5, tileY: 7, mapKey: 'pallet_town' });
  /** Shared dpad state object — Phaser reads this in update(). Stable reference. */
  const dpadRef = useRef<DpadReactive>({ up: false, down: false, left: false, right: false });
  /** Tracks which arrow keys are currently held (for visual highlight). */
  const [keysDown, setKeysDown] = useState<DpadReactive>({ up: false, down: false, left: false, right: false });

  /** Intenta cargar la partida existente al montar el componente. */
  useEffect(() => {
    gameService.loadSave().then((s) => {
      setSaveData(s);
      lastKnownPosRef.current = { tileX: s.tile_x ?? 5, tileY: s.tile_y ?? 7, mapKey: s.map_id ?? 'pallet_town' };
    }).catch(() => {
      setSaveData(null);
    });
  }, []);

  /** Keyboard arrow highlight + dpad sync for keyboard users. */
  useEffect(() => {
    const onDown = (e: KeyboardEvent) => {
      const dir = KEY_DIR[e.code];
      if (!dir) return;
      dpadRef.current[dir] = true;
      setKeysDown((prev) => prev[dir] ? prev : { ...prev, [dir]: true });
    };
    const onUp = (e: KeyboardEvent) => {
      const dir = KEY_DIR[e.code];
      if (!dir) return;
      dpadRef.current[dir] = false;
      setKeysDown((prev) => prev[dir] ? { ...prev, [dir]: false } : prev);
    };
    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    return () => {
      window.removeEventListener('keydown', onDown);
      window.removeEventListener('keyup', onUp);
    };
  }, []);

  const handleStart = useCallback(async () => {
    setStatus('loading');
    try {
      let save = saveData;
      if (!save) {
        // Primera vez: crear partida nueva
        save = await gameService.newGame();
        setSaveData(save);
      }
      setStatus('running');
    } catch (err: unknown) {
      console.error('Error al iniciar el juego:', err);
      setStatus('error');
    }
  }, [saveData]);

  const handleManualSave = useCallback(async () => {
    if (!saveData) return;
    setSaveStatus('saving');
    try {
      const { tileX, tileY, mapKey } = lastKnownPosRef.current;
      const updated = await gameService.saveGame({
        map_id: mapKey,
        tile_x: tileX,
        tile_y: tileY,
        play_time_seconds: (saveData.play_time_seconds ?? 0) + 1,
      });
      setSaveData(updated);
      setSaveStatus('idle');
    } catch {
      setSaveStatus('error');
    }
  }, [saveData]);

  const handleShutdown = useCallback(async () => {
    // Save current position then power off
    if (saveData) {
      const { tileX, tileY, mapKey } = lastKnownPosRef.current;
      try {
        await gameService.saveGame({ map_id: mapKey, tile_x: tileX, tile_y: tileY });
      } catch {
        // Don't block shutdown on save error
      }
    }
    setStatus('off');
    setSaveStatus('idle');
  }, [saveData]);

  /** Press a dpad direction (touch start). */
  const pressDpad = (dir: keyof DpadReactive) => { dpadRef.current[dir] = true; };
  /** Release a dpad direction (touch end / leave). */
  const releaseDpad = (dir: keyof DpadReactive) => { dpadRef.current[dir] = false; };

  return (
    <div className="game-shell">
      <div className="game-device">
        {/* ── Pantalla ─────────────────────────────────────────────── */}
        <div className="game-device__bezel">
          {status === 'off' && (
            <div className="game-device__screen--off">
              <div className="game-device__screen-dot" />
              <span className="game-device__screen-label">PokeTrainer</span>
            </div>
          )}

          {status === 'loading' && (
            <div className="game-device__screen--off">
              <div className="game-device__loading">
                <div className="game-device__loading-bar" />
                <span className="game-device__loading-text">Loading…</span>
              </div>
            </div>
          )}

          {status === 'error' && (
            <div className="game-device__screen--off">
              <span className="game-device__screen-label" style={{ color: '#ff6b6b' }}>
                Error
              </span>
            </div>
          )}

          {status === 'running' && (
            <div className="game-device__screen--active">
              <PhaserGame
                width={GAME_WIDTH}
                height={GAME_HEIGHT}
                initMapKey={saveData?.map_id ?? 'pallet_town'}
                initTileX={saveData?.tile_x ?? 5}
                initTileY={saveData?.tile_y ?? 7}
                dpadState={dpadRef.current}
                onSave={async (tileX, tileY, mapKey) => {
                  lastKnownPosRef.current = { tileX, tileY, mapKey };
                  try {
                    const updated = await gameService.saveGame({ map_id: mapKey, tile_x: tileX, tile_y: tileY });
                    setSaveData(updated);
                  } catch {
                    // silent autosave failure
                  }
                }}
              />

              {/* ── D-pad overlay ─────────────────────────────────── */}
              <div className="game-device__dpad-overlay" onContextMenu={(e) => e.preventDefault()}>
                <button
                  className={`dpad-btn dpad-btn--up${keysDown.up ? ' dpad-btn--active' : ''}`}
                  onPointerDown={() => pressDpad('up')}
                  onPointerUp={() => releaseDpad('up')}
                  onPointerLeave={() => releaseDpad('up')}
                  aria-label="Up"
                >▲</button>
                <button
                  className={`dpad-btn dpad-btn--left${keysDown.left ? ' dpad-btn--active' : ''}`}
                  onPointerDown={() => pressDpad('left')}
                  onPointerUp={() => releaseDpad('left')}
                  onPointerLeave={() => releaseDpad('left')}
                  aria-label="Left"
                >◀</button>
                <div className="dpad-center" />
                <button
                  className={`dpad-btn dpad-btn--right${keysDown.right ? ' dpad-btn--active' : ''}`}
                  onPointerDown={() => pressDpad('right')}
                  onPointerUp={() => releaseDpad('right')}
                  onPointerLeave={() => releaseDpad('right')}
                  aria-label="Right"
                >▶</button>
                <button
                  className={`dpad-btn dpad-btn--down${keysDown.down ? ' dpad-btn--active' : ''}`}
                  onPointerDown={() => pressDpad('down')}
                  onPointerUp={() => releaseDpad('down')}
                  onPointerLeave={() => releaseDpad('down')}
                  aria-label="Down"
                >▼</button>
              </div>
            </div>
          )}
        </div>

        {/* ── Marca ─────────────────────────────────────────────────── */}
        <span className="game-device__brand">PokeTrainer GB</span>

        {/* ── Controles ─────────────────────────────────────────────── */}
        <div className="game-device__controls">
          {status !== 'running' ? (
            <button
              className="game-device__start-btn"
              onClick={handleStart}
              disabled={status === 'loading'}
            >
              {saveData ? 'CONTINUE' : 'START'}
            </button>
          ) : (
            <div className="game-device__action-buttons">
              <button
                className="game-device__save-btn"
                onClick={handleManualSave}
                disabled={saveStatus === 'saving'}
              >
                SAVE
              </button>
              <button
                className="game-device__shutdown-btn"
                onClick={handleShutdown}
              >
                SHUT DOWN
              </button>
            </div>
          )}
        </div>

        {saveData && status === 'off' && (
          <p className="game-device__save-status">
            {saveData.map_id.replace('_', ' ')} · {Math.floor(saveData.play_time_seconds / 60)}m played
          </p>
        )}
      </div>
    </div>
  );
}
