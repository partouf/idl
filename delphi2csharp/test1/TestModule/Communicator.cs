namespace TestModule
{
    public class Communicator : ICommunicator
    {
        private int id { get; set; }

        public int GetID()
        {
            return id;
        }

        public void SetID(int ID)
        {
            id = ID;
        }
    }
}
