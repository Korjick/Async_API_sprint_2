import uuid
import datetime

from testdata.genres_data import genres_data


def _build_genre_index() -> dict[str, str]:
    """Индекс жанров по имени: name -> id (строго по genres_data)."""
    return {g["name"]: g["id"] for g in genres_data}


GENRE_ID_BY_NAME = _build_genre_index()


def genre_obj(name: str) -> dict:
    return {"id": GENRE_ID_BY_NAME[name], "name": name}


films_data = [
    {
        "id": "6e5cd268-8ce4-45f9-87d2-52f0f26edc9e",
        "imdb_rating": 7.7,
        "title": "The Wrath of Khan",
        "description": "It is the 23rd century. Admiral James T. Kirk is an instructor at Starfleet Academy and feeling old; the prospect of attending his ship, the USS Enterprise--now a training ship--on a two-week cadet cruise does not make him feel any younger. But the training cruise becomes a deadly serious mission when his nemesis Khan Noonien Singh--infamous conqueror from late 20th century Earth--appears after years of exile. Khan later revealed that the planet Ceti Alpha VI exploded, and shifted the orbit of the fifth planet as a Mars-like haven. He begins capturing Project Genesis, a top secret device holding the power of creation itself, and schemes the utter destruction of Kirk.",
        "genres": [
            genre_obj("Adventure"),
            genre_obj("Action"),
            genre_obj("Sci-Fi"),
        ],
        "directors": [
            {"id": "c883c2c6-d7a4-4001-8084-e2851904e91a", "name": "Nicholas Meyer"}
        ],
        "actors": [
            {"id": "5a3d0299-2df2-4070-9fda-65ff4dfa863c", "name": "Leonard Nimoy"},
            {"id": "807ce9c3-6294-485c-803a-1975066f239f", "name": "James Doohan"},
            {"id": "836bb95b-6db8-4418-a110-f41663b1c025", "name": "DeForest Kelley"},
            {"id": "9758b894-57d7-465d-b657-c5803dd5b7f7", "name": "William Shatner"},
        ],
        "writers": [
            {"id": "24b5b1fb-9931-4964-a0d2-ce664c00c1d5", "name": "Jack B. Sowards"},
            {"id": "58411ec0-c40a-43da-95e3-0adc74b7e7f6", "name": "Harve Bennett"},
            {"id": "6960e2ca-889f-41f5-b728-1e7313e54d6c", "name": "Gene Roddenberry"},
        ],
        "directors_names": ["Nicholas Meyer"],
        "actors_names": [
            "Leonard Nimoy",
            "James Doohan",
            "DeForest Kelley",
            "William Shatner",
        ],
        "writers_names": ["Jack B. Sowards", "Harve Bennett", "Gene Roddenberry"],
    },
    {
        "id": "b1384a92-f7fe-476b-b90b-6cec2b7a0dce",
        "imdb_rating": 8.6,
        "title": "The Next Generation",
        "description": "Set in the 24th century and decades after the adventures of the original crew of the starship Enterprise, this new series is the long-awaited successor to the original Star Trek (1966). Under the command of Captain Jean-Luc Picard, the all new Enterprise NCC 1701-D travels out to distant planets to seek out new life and to boldly go where no one has gone before.",
        "genres": [
            genre_obj("Adventure"),
            genre_obj("Action"),
            genre_obj("Sci-Fi"),
            genre_obj("Mystery"),
        ],
        "directors": [],
        "actors": [
            {"id": "035c4793-4864-45b8-8d4f-b86b454c60b0", "name": "Marina Sirtis"},
            {"id": "57a471b1-09dc-48fd-ba8a-1211015a0110", "name": "Patrick Stewart"},
            {"id": "5bddea2c-8609-499a-a444-77e0142743c0", "name": "Jonathan Frakes"},
            {"id": "fc9f27d2-aaee-46e6-b263-40ec8d2dd355", "name": "LeVar Burton"},
        ],
        "writers": [
            {"id": "6960e2ca-889f-41f5-b728-1e7313e54d6c", "name": "Gene Roddenberry"}
        ],
        "directors_names": [],
        "actors_names": [
            "Marina Sirtis",
            "Patrick Stewart",
            "Jonathan Frakes",
            "LeVar Burton",
        ],
        "writers_names": ["Gene Roddenberry"],
    },
    {
        "id": "c9e1f6f0-4f1e-4a76-92ee-76c1942faa97",
        "imdb_rating": 7.3,
        "title": "Star Trek: Discovery",
        "description": "Ten years before Kirk, Spock, and the Enterprise, the USS Discovery discovers new worlds and lifeforms as one Starfleet officer learns to understand all things alien.",
        "genres": [
            genre_obj("Adventure"),
            genre_obj("Drama"),
            genre_obj("Action"),
            genre_obj("Sci-Fi"),
        ],
        "directors": [],
        "actors": [
            {"id": "3f123595-ecfb-4740-a1c5-ceab9fc21c23", "name": "Anthony Rapp"},
            {"id": "43bb73ff-0f0e-4169-b708-32a77dc1c50e", "name": "Doug Jones"},
            {"id": "861a3116-7f75-4b7c-b1a1-5efd4936589c", "name": "Mary Wiseman"},
            {"id": "bd2a8ab8-a7bc-45cf-852b-d23cb1cf4b5d", "name": "Sonequa Martin-Green"},
        ],
        "writers": [
            {"id": "82b7dffe-6254-4598-b6ef-5be747193946", "name": "Alex Kurtzman"},
            {"id": "b670fa3e-9f7b-4786-a00c-09d95f1e7b5c", "name": "Bryan Fuller"},
        ],
        "directors_names": [],
        "actors_names": [
            "Anthony Rapp",
            "Doug Jones",
            "Mary Wiseman",
            "Sonequa Martin-Green",
        ],
        "writers_names": ["Alex Kurtzman", "Bryan Fuller"],
    },
    {
        "id": "37c6cd37-1222-4470-9221-3170367d134b",
        "imdb_rating": 6.7,
        "title": "The Search for Spock",
        "description": "In the wake of Spock's ultimate deed of sacrifice, Admiral Kirk and the Enterprise crew return to Earth for some essential repairs to their ship. When they arrive at Spacedock, they are shocked to discover that the Enterprise is to be decommissioned. Even worse, Dr. McCoy begins acting strangely and Scotty has been reassigned to another ship. Kirk is forced to steal back the Enterprise and head across space to the Genesis Planet to save Spock and bring him to Vulcan. Unknown to them, the Klingons are planning to steal the secrets of the Genesis Device for their own deadly purpose.",
        "genres": [
            genre_obj("Adventure"),
            genre_obj("Action"),
            genre_obj("Sci-Fi"),
        ],
        "directors": [
            {"id": "5a3d0299-2df2-4070-9fda-65ff4dfa863c", "name": "Leonard Nimoy"}
        ],
        "actors": [
            {"id": "5a3d0299-2df2-4070-9fda-65ff4dfa863c", "name": "Leonard Nimoy"},
            {"id": "807ce9c3-6294-485c-803a-1975066f239f", "name": "James Doohan"},
            {"id": "836bb95b-6db8-4418-a110-f41663b1c025", "name": "DeForest Kelley"},
            {"id": "9758b894-57d7-465d-b657-c5803dd5b7f7", "name": "William Shatner"},
        ],
        "writers": [
            {"id": "58411ec0-c40a-43da-95e3-0adc74b7e7f6", "name": "Harve Bennett"},
            {"id": "6960e2ca-889f-41f5-b728-1e7313e54d6c", "name": "Gene Roddenberry"},
        ],
        "directors_names": ["Leonard Nimoy"],
        "actors_names": [
            "Leonard Nimoy",
            "James Doohan",
            "DeForest Kelley",
            "William Shatner",
        ],
        "writers_names": ["Harve Bennett", "Gene Roddenberry"],
    },
]

for i in range(60):
    films_data.append(
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 7.0 + (i % 3) * 0.5,
            "genres": [genre_obj("Action"), genre_obj("Sci-Fi")],
            "title": f"Test Movie {i+1}",
            "description": f"Test description {i+1}",
            "actors_names": [f"Actor {i}"],
            "writers_names": [f"Writer {i}"],
            "directors_names": [f"Director {i}"],
            "directors": [{"id": str(uuid.uuid4()), "name": f"Director {i}"}],
            "actors": [
                {"id": str(uuid.uuid4()), "name": f"Actor {i}"},
                {"id": str(uuid.uuid4()), "name": f"Actor {i+1}"},
            ],
            "writers": [
                {"id": str(uuid.uuid4()), "name": f"Writer {i}"},
                {"id": str(uuid.uuid4()), "name": f"Writer {i+1}"},
            ],
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "film_work_type": "movie",
        }
    )
