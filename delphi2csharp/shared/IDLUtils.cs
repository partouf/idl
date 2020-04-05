namespace IDLInterop
{
    using Unity;

    public static class InteropContainer
    {
        private static IUnityContainer Default = new UnityContainer();

        public static void RegisterType<TFrom, TTo>() where TTo : TFrom
        {
            UnityContainerExtensions.RegisterType<TFrom, TTo>(Default);
        }

        public static T Resolve<T>()
        {
            return UnityContainerExtensions.Resolve<T>(Default);
        }
    }
}
