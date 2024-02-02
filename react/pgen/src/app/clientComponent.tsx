'use client'

import { useFormState, useFormStatus } from "react-dom";
import { loginAction, searchAction } from "./serverComponents";
import { useEffect, useState } from "react";

const SubmitButton = ({id, defaultText, pendingText}: {id: string, defaultText: string, pendingText: string}) => {
	const { pending } = useFormStatus();

	return (
		<button hidden={defaultText === ''} id={id} type='submit' aria-disabled={pending} disabled={pending}>
			{pending && pendingText || !pending && defaultText}
		</button>
	)
}

export default function ClientComponent({loggedIn}: {loggedIn: boolean}) {
  const [loginState, formLoginAction] = useFormState(loginAction, {});
  const [searchState, formSearchAction] = useFormState(searchAction, {error: '', object: [], status: 0});
  const [artistsFound, setArtistsFound] = useState(false)
  const [inputValue, setInputValue] = useState('');
  const [artists, setArtists] = useState<any[]>([]); // Lista de artistas original
  const [draggedArtist, setDraggedArtist] = useState<any | null>(null); // Artista que se está arrastrando

  const handleMouseDown = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    setDraggedArtist(event.currentTarget);
  };
  
  const handleMouseMove = (event: MouseEvent) => {
    console.log(draggedArtist)
    if (draggedArtist) {
      // Actualiza la posición del elemento arrastrado
      draggedArtist.style.left = `${event.pageX}px`;
      draggedArtist.style.top = `${event.pageY}px`;
    }
  };
  
  const handleMouseUp = () => {
    setDraggedArtist(null);
  };

  useEffect(() => {
    // Agregar eventos de mouse globales para manejar el arrastrar y soltar
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      // Limpiar eventos de mouse cuando el componente se desmonte
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [draggedArtist]);

  const handleInputChange = (event: any) => {
    setInputValue(event.target.value);
    if (event.target.value === '') {
      searchState.object = []
    }
  };

  const handleClearButtonClick = () => {
    setInputValue('');
    searchState.object = []
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (inputValue !== '') {
        document.getElementById('searchButton')?.click();
      }
    }, 500);
  
    return () => clearTimeout(timeoutId); // Limpiar el timeout en cada renderización
  }, [inputValue]);

  useEffect(() => {
    setArtistsFound(searchState.object.length !== 0)
  }, [searchState.object])

  return (
<div className="max-w-lg mx-auto flex">
  {!loggedIn && (
    <form action={formLoginAction} className="mb-4">
      <SubmitButton id='loginButton' defaultText="Inicia sesión con Spotify" pendingText="Serás redirigido en breve..." />
    </form>
  )}

  {loggedIn && (<>
    <div className="w-1/2">
    <form action={formSearchAction} className="mb-4">
      <div className="flex items-center border rounded-md overflow-hidden">
        <input
          autoComplete="off"
          id="query"
          name="query"
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          className="py-2 px-4 flex-grow focus:outline-none"
          placeholder="Buscar..."
        />
        {inputValue && (
          <button
            onClick={handleClearButtonClick}
            className="bg-gray-300 text-gray-600 px-4 focus:outline-none hover:bg-gray-400"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      <SubmitButton id='searchButton' defaultText="" pendingText="" />
    </form>

    <div className="mb-4">
    {artistsFound &&
    
      searchState.object.map((value: any) => (
        <div
          key={value.id}
          className="flex items-center bg-white rounded-lg p-4 hover:shadow-lg cursor-pointer mb-4 border border-gray-300"
          onMouseDown={handleMouseDown}
          style={{ position: 'absolute' }} // Cambia la posición a absoluta para que puedas moverlos libremente
        >
          <img src={value.image.url} alt={value.name} className="h-16 w-16 rounded-full mr-4" />
          <p className="text-lg">{value.name}</p>
        </div>
      ))}
      </div>
  </div>

  <div
    className="w-1/2 border rounded-md p-4"
  >
    <h2>Artistas seleccionados:</h2>
    <ul>
      {/* {selectedArtists.map((artist, index) => (
        <li key={index}>{artist}</li>
      ))} */}
    </ul>
  </div>
  </>)}
</div>

  );
}
