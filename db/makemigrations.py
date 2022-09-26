from tables import Base, engine

if __name__ == '__main__':
    print('making migrations')
    Base.metadata.create_all(engine)