
%struct.b = type {[23 x i32]}

define %struct.b @func.f(%struct.b %c, i32 %a) {
    %c.ptr = alloca %struct.b
    %a.ptr = alloca i32
    store %struct.b %c, %struct.b* %c.ptr
    store i32 %a, i32* %a.ptr
    %struct.b.0.1.ptr = getelementptr inbounds %struct.b, %struct.b* %c.ptr, i32 0, i32 0
    %struct.b.0.1.1.ptr = getelementptr inbounds [23 x i32], [23 x i32]* %struct.b.0.1.ptr, i32 0, i32 2
    store i32 3, i32* %struct.b.0.1.1.ptr
    %c.3 = load %struct.b, %struct.b* %c.ptr
    ret %struct.b %c.3
}

define i32 @main() {
    %str.ptr = alloca i8*
    store i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.1, i32 0, i32 0), i8** %str.ptr
    %ss.ptr = alloca %struct.b
    %struct.b.0.4.ptr = getelementptr inbounds %struct.b, %struct.b* %ss.ptr, i32 0, i32 0
    %struct.b.0.4.4.ptr = getelementptr inbounds [23 x i32], [23 x i32]* %struct.b.0.4.ptr, i32 0, i32 2
    store i32 5, i32* %struct.b.0.4.4.ptr
    %ss.6 = load %struct.b, %struct.b* %ss.ptr
    %f.7 = call %struct.b @func.f(%struct.b %ss.6, i32 2)
    %f.8.ptr = alloca %struct.b
    store %struct.b %f.7, %struct.b* %f.8.ptr
    %struct.b.0.9.ptr = getelementptr inbounds %struct.b, %struct.b* %f.8.ptr, i32 0, i32 0
    %struct.b.0.9.9.ptr = getelementptr inbounds [23 x i32], [23 x i32]* %struct.b.0.9.ptr, i32 0, i32 2
    %struct.b.0.9.9.11 = load i32, i32* %struct.b.0.9.9.ptr
    %buffer13 = getelementptr inbounds [4 x i8], [4 x i8]* @.str.2, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer13, i32 %struct.b.0.9.9.11)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"123\00", align 1
@.str.2 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
